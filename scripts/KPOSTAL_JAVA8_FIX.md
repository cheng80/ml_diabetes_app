# kpostal 사용 프로젝트 — Java 8 경고 해결 가이드

`kpostal`을 사용하는 Flutter 프로젝트에서 Android 빌드 시 발생하는
`source value 8 is obsolete` / `target value 8 is obsolete` 경고를 제거하는 방법입니다.

---

## 증상

```
warning: [options] source value 8 is obsolete and will be removed in a future release
warning: [options] target value 8 is obsolete and will be removed in a future release
warning: [options] To suppress warnings about obsolete options, use -Xlint:-options.
```

빌드는 성공하지만 위 경고가 반복 출력됩니다.

---

## 원인

`kpostal ^1.1.0`의 전이 의존성 중 일부 Android 플러그인이 `build.gradle`에서
`JavaVersion.VERSION_1_8`을 사용합니다.  
최신 JDK + Gradle 환경에서는 Java 8 타겟이 obsolete로 취급됩니다.

### 경고를 발생시키는 플러그인

| 플러그인 | 의존 경로 | 해당 버전 Java 설정 |
|---|---|---|
| `geocoding_android` 3.3.1 | `kpostal` → `geocoding` → `geocoding_android` | `VERSION_1_8` |
| `flutter_inappwebview_android` 1.1.3 | `kpostal` → `flutter_inappwebview` → `flutter_inappwebview_android` | 미지정 (기본값 1.8) |

`kpostal`이 `geocoding: ^3.0.0`으로 고정하고 있어, Java 11로 수정된
`geocoding_android 5.0.0` (`geocoding_platform_interface ^4.0.0` 필요)으로 올릴 수 없습니다.

### map_launcher를 함께 사용하는 경우

`map_launcher` 3.x도 동일하게 Java 1.8 + AGP 7.3.0을 사용합니다.
4.0.0 이상에서 Java 11 + AGP 8.7.3으로 수정되었으므로 업그레이드로 해결 가능합니다.

---

## 해결 방법

두 단계로 나뉩니다.

### 1단계: map_launcher 업그레이드 (해당 시)

`map_launcher`를 사용하는 프로젝트라면 `pubspec.yaml`에서 버전을 올립니다.

```yaml
# Before
map_launcher: ^3.5.0

# After
map_launcher: ^4.4.3
```

> **API 호환성**: `MapLauncher.installedMaps`, `map.showDirections()`, `map.showMarker()`,
> `map.icon`, `map.mapName` 등 주요 API는 4.x에서도 동일합니다.
> 단, 4.0.0에서 내부 구조가 재작성되었으므로 빌드 후 동작 확인을 권장합니다.

```bash
flutter pub get
```

### 2단계: android/build.gradle.kts에 Java 11 강제 적용

`kpostal` 전이 의존성(`geocoding_android`, `flutter_inappwebview_android`)은
`kpostal`이 업데이트되기 전까지 버전을 올릴 수 없으므로,
**루트 `build.gradle.kts`에서 해당 모듈의 Java 버전을 강제 오버라이드**합니다.

`android/build.gradle.kts` 파일의 `tasks.register<Delete>("clean")` **직전**에
아래 블록을 추가합니다:

```kotlin
// Upgrade Java 1.8 → 11 for specific third-party plugins that still declare Java 1.8,
// suppressing "source/target value 8 is obsolete" warnings.
val java8Modules = setOf("geocoding_android", "flutter_inappwebview_android")
subprojects {
    if (name in java8Modules) {
        afterEvaluate {
            extensions.findByType<com.android.build.gradle.BaseExtension>()?.compileOptions {
                sourceCompatibility = JavaVersion.VERSION_11
                targetCompatibility = JavaVersion.VERSION_11
            }
        }
    }
}
```

#### 왜 afterEvaluate인가?

각 플러그인의 `build.gradle`이 먼저 `VERSION_1_8`을 설정하므로,
`afterEvaluate`로 평가 완료 후 덮어써야 합니다.

#### 왜 특정 모듈만 지정하는가?

`package_info_plus` 등 이미 Java 17 + Kotlin 17로 설정된 모듈을
Java 11로 내려버리면 Kotlin과 JVM 타겟 불일치 오류가 발생합니다:

```
Inconsistent JVM-target compatibility detected for tasks
'compileDebugJavaWithJavac' (11) and 'compileDebugKotlin' (17).
```

따라서 **Java 1.8인 모듈만** 명시적으로 나열하여 적용합니다.

---

## 전체 적용 예시

### android/build.gradle.kts (발췌)

```kotlin
// ... 기존 allprojects, subprojects 블록들 ...

// Upgrade Java 1.8 → 11 for specific third-party plugins that still declare Java 1.8,
// suppressing "source/target value 8 is obsolete" warnings.
val java8Modules = setOf("geocoding_android", "flutter_inappwebview_android")
subprojects {
    if (name in java8Modules) {
        afterEvaluate {
            extensions.findByType<com.android.build.gradle.BaseExtension>()?.compileOptions {
                sourceCompatibility = JavaVersion.VERSION_11
                targetCompatibility = JavaVersion.VERSION_11
            }
        }
    }
}

tasks.register<Delete>("clean") {
    delete(rootProject.layout.buildDirectory)
}
```

### 빌드 확인

```bash
flutter clean
flutter pub get
flutter build apk --debug
```

경고 없이 빌드되면 성공입니다.

---

## 다른 프로젝트에 적용하기

1. 해당 프로젝트의 `android/build.gradle.kts` (또는 `build.gradle`) 확인
2. `kpostal` 전이 의존성 중 Java 1.8 모듈을 식별:
   ```bash
   # .flutter-plugins-dependencies의 android 플러그인 경로에서 확인
   grep -r "VERSION_1_8" ~/.pub-cache/hosted/pub.dev/geocoding_android-*/android/build.gradle
   grep -r "VERSION_1_8" ~/.pub-cache/hosted/pub.dev/flutter_inappwebview_android-*/android/build.gradle
   ```
3. 식별된 모듈 이름을 `java8Modules`에 추가
4. 위 Kotlin DSL 블록을 `build.gradle.kts`에 붙여넣기
5. 빌드 확인

### build.gradle (Groovy DSL) 프로젝트인 경우

`build.gradle.kts`가 아닌 `build.gradle`을 사용하는 프로젝트라면:

```groovy
// android/build.gradle 에 추가
def java8Modules = ['geocoding_android', 'flutter_inappwebview_android'] as Set

subprojects {
    if (java8Modules.contains(project.name)) {
        afterEvaluate {
            if (project.hasProperty('android')) {
                android {
                    compileOptions {
                        sourceCompatibility JavaVersion.VERSION_11
                        targetCompatibility JavaVersion.VERSION_11
                    }
                }
            }
        }
    }
}
```

---

## 장기 해결 전망

| 조건 | 기대 효과 |
|---|---|
| `kpostal`이 `geocoding ^4.0.0+` 의존으로 업데이트 | `geocoding_android` 5.0.0 사용 가능 → Java 11 기본 |
| `flutter_inappwebview_android` 새 버전에서 Java 11 명시 | 자동 해소 |
| 위 업데이트 적용 후 | `java8Modules`에서 해당 모듈 제거 가능 |

---

## 트러블슈팅

| 증상 | 원인 | 대응 |
|---|---|---|
| `Inconsistent JVM-target compatibility` | Java 17 모듈을 11로 내림 | `java8Modules`에 해당 모듈이 포함되어 있는지 확인, 제거 |
| `Cannot run afterEvaluate when already evaluated` | `:app` 모듈에 적용됨 | `if (name != "app")` 조건 추가 또는 모듈 명시 방식 사용 |
| `sourceCompatibility is not yet finalized` | 일부 모듈이 compileOptions 미설정 | 해당 모듈을 `java8Modules`에 명시적으로 추가 |
| 패치 후에도 경고 발생 | 다른 플러그인에서도 Java 1.8 사용 | `flutter build apk --debug 2>&1 \| grep "source value 8"` 후 해당 모듈 식별하여 추가 |
