import 'package:glucoinsight/theme/app_theme_colors.dart';
import 'package:glucoinsight/theme/theme_provider.dart';
import 'package:glucoinsight/utils/app_storage.dart';
import 'package:glucoinsight/view/main_tab_page.dart';
import 'package:flutter/material.dart';
import 'package:get_storage/get_storage.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await GetStorage.init();
  runApp(const MyApp());
}

class MyApp extends StatefulWidget {
  const MyApp({super.key});

  @override
  State<MyApp> createState() => _MyAppState();
}

class _MyAppState extends State<MyApp> {
  late ThemeMode _themeMode;

  @override
  void initState() {
    super.initState();
    _themeMode = _loadThemeMode();
  }

  ThemeMode _loadThemeMode() {
    final saved = AppStorage.getThemeMode();
    if (saved == null) return ThemeMode.light;
    switch (saved) {
      case 'light':
        return ThemeMode.light;
      case 'dark':
        return ThemeMode.dark;
      case 'system':
        return ThemeMode.system;
      default:
        return ThemeMode.light;
    }
  }

  void _toggleTheme() {
    setState(() {
      _themeMode =
          _themeMode == ThemeMode.light ? ThemeMode.dark : ThemeMode.light;
      AppStorage.saveThemeMode(_themeMode.name);
    });
  }

  @override
  Widget build(BuildContext context) {
    return ThemeProvider(
      themeMode: _themeMode,
      onToggleTheme: _toggleTheme,
      child: MaterialApp(
        debugShowCheckedModeBanner: false,
        title: '당뇨 예측 앱',
        theme: ThemeData(
          brightness: Brightness.light,
          scaffoldBackgroundColor: AppThemeColors.lightBackground,
          colorScheme: ColorScheme.fromSeed(
            seedColor: const Color(0xFF1976D2),
            brightness: Brightness.light,
            primary: const Color(0xFF1976D2),
            surface: const Color(0xFFF5F5F5),
          ),
          useMaterial3: true,
          textButtonTheme: TextButtonThemeData(
            style: ButtonStyle(
              textStyle: WidgetStatePropertyAll(
                const TextStyle(fontWeight: FontWeight.bold),
              ),
            ),
          ),
          filledButtonTheme: FilledButtonThemeData(
            style: ButtonStyle(
              textStyle: WidgetStatePropertyAll(
                const TextStyle(fontWeight: FontWeight.bold),
              ),
            ),
          ),
          outlinedButtonTheme: OutlinedButtonThemeData(
            style: ButtonStyle(
              textStyle: WidgetStatePropertyAll(
                const TextStyle(fontWeight: FontWeight.bold),
              ),
            ),
          ),
          elevatedButtonTheme: ElevatedButtonThemeData(
            style: ButtonStyle(
              textStyle: WidgetStatePropertyAll(
                const TextStyle(fontWeight: FontWeight.bold),
              ),
            ),
          ),
          listTileTheme: ListTileThemeData(
            titleTextStyle: const TextStyle(
              fontWeight: FontWeight.bold,
              color: Color(0xFF212121),
            ),
            subtitleTextStyle: const TextStyle(
              fontWeight: FontWeight.bold,
              color: Color(0xFF616161),
            ),
          ),
          bottomNavigationBarTheme: const BottomNavigationBarThemeData(
            selectedItemColor: Color(0xFF1976D2),
            unselectedItemColor: Color(0xFF757575),
            selectedLabelStyle: TextStyle(fontWeight: FontWeight.bold),
            unselectedLabelStyle: TextStyle(fontWeight: FontWeight.bold),
          ),
          appBarTheme: const AppBarThemeData(
            backgroundColor: Color(0xFFF5F5F5),
            foregroundColor: Color(0xFF212121),
            titleTextStyle: TextStyle(
              fontWeight: FontWeight.bold,
              fontSize: 20,
              color: Color(0xFF212121),
            ),
            iconTheme: IconThemeData(color: Color(0xFF212121)),
          ),
        ),
        darkTheme: ThemeData(
          brightness: Brightness.dark,
          scaffoldBackgroundColor: AppThemeColors.darkBackground,
          colorScheme: ColorScheme.fromSeed(
            seedColor: const Color(0xFF1976D2),
            brightness: Brightness.dark,
            primary: const Color(0xFF64B5F6),
            onPrimary: const Color(0xFF0D47A1),
            surface: const Color.fromRGBO(26, 26, 26, 1),
          ),
          useMaterial3: true,
          textButtonTheme: TextButtonThemeData(
            style: ButtonStyle(
              textStyle: WidgetStatePropertyAll(
                const TextStyle(fontWeight: FontWeight.bold),
              ),
            ),
          ),
          filledButtonTheme: FilledButtonThemeData(
            style: ButtonStyle(
              textStyle: WidgetStatePropertyAll(
                const TextStyle(fontWeight: FontWeight.bold),
              ),
            ),
          ),
          outlinedButtonTheme: OutlinedButtonThemeData(
            style: ButtonStyle(
              textStyle: WidgetStatePropertyAll(
                const TextStyle(fontWeight: FontWeight.bold),
              ),
            ),
          ),
          elevatedButtonTheme: ElevatedButtonThemeData(
            style: ButtonStyle(
              textStyle: WidgetStatePropertyAll(
                const TextStyle(fontWeight: FontWeight.bold),
              ),
            ),
          ),
          listTileTheme: ListTileThemeData(
            titleTextStyle: const TextStyle(
              fontWeight: FontWeight.bold,
              color: Colors.white,
            ),
            subtitleTextStyle: const TextStyle(
              fontWeight: FontWeight.bold,
              color: Color(0xFFBDBDBD),
            ),
          ),
          bottomNavigationBarTheme: const BottomNavigationBarThemeData(
            selectedItemColor: Color(0xFF64B5F6),
            unselectedItemColor: Color(0xFF9E9E9E),
            selectedLabelStyle: TextStyle(fontWeight: FontWeight.bold),
            unselectedLabelStyle: TextStyle(fontWeight: FontWeight.bold),
          ),
          appBarTheme: const AppBarThemeData(
            backgroundColor: Color.fromRGBO(26, 26, 26, 1),
            foregroundColor: Colors.white,
            titleTextStyle: TextStyle(
              fontWeight: FontWeight.bold,
              fontSize: 20,
              color: Colors.white,
            ),
            iconTheme: IconThemeData(color: Colors.white),
          ),
        ),
        themeMode: _themeMode,
        home: const MainTabPage(),
      ),
    );
  }
}
