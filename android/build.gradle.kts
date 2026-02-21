allprojects {
    repositories {
        google()
        mavenCentral()
    }
}

val newBuildDir: Directory =
    rootProject.layout.buildDirectory
        .dir("../../build")
        .get()
rootProject.layout.buildDirectory.value(newBuildDir)

subprojects {
    val newSubprojectBuildDir: Directory = newBuildDir.dir(project.name)
    project.layout.buildDirectory.value(newSubprojectBuildDir)
}
subprojects {
    project.evaluationDependsOn(":app")
}

// AGP 8+ compatibility patch:
// Some old Android plugins from pub cache do not declare `namespace`.
// Set a fallback namespace for Android modules when missing.
subprojects {
    fun setFallbackNamespaceIfMissing() {
        val androidExt = extensions.findByName("android") ?: return
        try {
            val getNamespace = androidExt.javaClass.getMethod("getNamespace")
            val currentNs = getNamespace.invoke(androidExt) as? String
            if (currentNs.isNullOrBlank()) {
                val setNamespace = androidExt.javaClass.getMethod("setNamespace", String::class.java)
                val fallbackNs = "dev.cursor.${project.name.replace('-', '_')}"
                setNamespace.invoke(androidExt, fallbackNs)
            }
        } catch (_: Exception) {
            // No-op for modules that do not expose namespace accessors.
        }
    }

    plugins.withId("com.android.library") { setFallbackNamespaceIfMissing() }
    plugins.withId("com.android.application") { setFallbackNamespaceIfMissing() }
}

tasks.register<Delete>("clean") {
    delete(rootProject.layout.buildDirectory)
}
