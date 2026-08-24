import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

// ← Cambia esta IP por la de tu PC cuando pruebes desde el celular
const String API_BASE = 'http://192.168.1.105:8080';

void main() {
  runApp(const FundoBerlinApp());
}

class FundoBerlinApp extends StatelessWidget {
  const FundoBerlinApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Fundo Berlín',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF2E7D32)),
        useMaterial3: true,
      ),
      home: const MainScreen(),
    );
  }
}

// ─────────────────────────────────────────
// NAVEGACIÓN PRINCIPAL
// ─────────────────────────────────────────
class MainScreen extends StatefulWidget {
  const MainScreen({super.key});

  @override
  State<MainScreen> createState() => _MainScreenState();
}

class _MainScreenState extends State<MainScreen> {
  int _currentIndex = 0;

  final List<Widget> _screens = const [
    InicioScreen(),
    LotesScreen(),
    NotificacionesScreen(),
    RegistrosScreen(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: _screens[_currentIndex],
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: (i) => setState(() => _currentIndex = i),
        type: BottomNavigationBarType.fixed,
        selectedItemColor: const Color(0xFF2E7D32),
        unselectedItemColor: Colors.grey,
        items: const [
          BottomNavigationBarItem(icon: Icon(Icons.home), label: 'Inicio'),
          BottomNavigationBarItem(icon: Icon(Icons.grid_view), label: 'Lotes'),
          BottomNavigationBarItem(icon: Icon(Icons.notifications), label: 'Alertas'),
          BottomNavigationBarItem(icon: Icon(Icons.list_alt), label: 'Registros'),
        ],
      ),
    );
  }
}

// ─────────────────────────────────────────
// PANTALLA INICIO
// ─────────────────────────────────────────
class InicioScreen extends StatefulWidget {
  const InicioScreen({super.key});

  @override
  State<InicioScreen> createState() => _InicioScreenState();
}

class _InicioScreenState extends State<InicioScreen> {
  Map<String, dynamic>? data;
  bool loading = true;

  @override
  void initState() {
    super.initState();
    _cargar();
  }

  Future<void> _cargar() async {
    try {
      final res = await http.get(Uri.parse('$API_BASE/api/inicio'));
      setState(() {
        data = jsonDecode(res.body);
        loading = false;
      });
    } catch (e) {
      setState(() => loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final analisis = data?['ultimo_analisis'];
    final sensor   = data?['ultimo_sensor'];
    final resultado = analisis?['resultado_ia'] ?? 'Sin datos';
    final esSano   = resultado == 'Café Sano';

    return Scaffold(
      appBar: AppBar(
        backgroundColor: const Color(0xFF2E7D32),
        title: const Text('Fundo Berlín', style: TextStyle(color: Colors.white)),
      ),
      body: loading
          ? const Center(child: CircularProgressIndicator())
          : RefreshIndicator(
              onRefresh: _cargar,
              child: ListView(
                padding: const EdgeInsets.all(16),
                children: [
                  // Estado general
                  Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(20),
                    decoration: BoxDecoration(
                      color: esSano ? const Color(0xFF2E7D32) : Colors.red[700],
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          esSano ? '✓ Café Sano' : '⚠ ${resultado}',
                          style: const TextStyle(color: Colors.white, fontSize: 22, fontWeight: FontWeight.bold),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          'Confianza: ${((analisis?['confianza_ia'] ?? 0) * 100).toStringAsFixed(1)}%',
                          style: const TextStyle(color: Colors.white70, fontSize: 14),
                        ),
                      ],
                    ),
                  ),

                  const SizedBox(height: 16),

                  // Sensor de suelo
                  _Tarjeta(
                    titulo: 'Estado del Suelo',
                    contenido: sensor?['estado_suelo'] ?? 'Sin datos',
                    icono: Icons.water_drop,
                    color: sensor?['estado_suelo'] == 'Húmedo'
                        ? Colors.blue[700]!
                        : Colors.orange[700]!,
                  ),

                  const SizedBox(height: 12),

                  // Última lectura
                  _Tarjeta(
                    titulo: 'Última lectura',
                    contenido: analisis?['fecha_hora'] ?? 'Sin datos',
                    icono: Icons.access_time,
                    color: Colors.grey[700]!,
                  ),

                  const SizedBox(height: 12),

                  // Próximas capturas
                  _Tarjeta(
                    titulo: 'Próximas capturas',
                    contenido: '09:00 y 15:00',
                    icono: Icons.schedule,
                    color: const Color(0xFF2E7D32),
                  ),
                ],
              ),
            ),
    );
  }
}

// ─────────────────────────────────────────
// PANTALLA LOTES
// ─────────────────────────────────────────
class LotesScreen extends StatefulWidget {
  const LotesScreen({super.key});

  @override
  State<LotesScreen> createState() => _LotesScreenState();
}

class _LotesScreenState extends State<LotesScreen> {
  List<dynamic> lotes = [];
  bool loading = true;

  @override
  void initState() {
    super.initState();
    _cargar();
  }

  Future<void> _cargar() async {
    try {
      final res = await http.get(Uri.parse('$API_BASE/api/lotes'));
      setState(() {
        lotes   = jsonDecode(res.body);
        loading = false;
      });
    } catch (e) {
      setState(() => loading = false);
    }
  }

  Color _colorEstado(String estado) {
    switch (estado) {
      case 'Alarma': return Colors.red[100]!;
      case 'Alerta': return Colors.orange[100]!;
      default:       return Colors.green[100]!;
    }
  }

  Color _colorBorde(String estado) {
    switch (estado) {
      case 'Alarma': return Colors.red;
      case 'Alerta': return Colors.orange;
      default:       return Colors.green;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: const Color(0xFF2E7D32),
        title: const Text('Lotes', style: TextStyle(color: Colors.white)),
      ),
      body: loading
          ? const Center(child: CircularProgressIndicator())
          : GridView.builder(
              padding: const EdgeInsets.all(16),
              gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                crossAxisCount: 2,
                crossAxisSpacing: 12,
                mainAxisSpacing: 12,
              ),
              itemCount: lotes.length,
              itemBuilder: (ctx, i) {
                final lote  = lotes[i];
                final estado = lote['estado'] ?? 'Saludable';
                return Container(
                  decoration: BoxDecoration(
                    color: _colorEstado(estado),
                    border: Border.all(color: _colorBorde(estado), width: 2),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  padding: const EdgeInsets.all(12),
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text(lote['nombre'], style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
                      const SizedBox(height: 8),
                      Text('Estado: ${estado}', style: const TextStyle(fontSize: 12)),
                      Text('Suelo: ${lote['humedad']}', style: const TextStyle(fontSize: 12)),
                    ],
                  ),
                );
              },
            ),
    );
  }
}

// ─────────────────────────────────────────
// PANTALLA NOTIFICACIONES
// ─────────────────────────────────────────
class NotificacionesScreen extends StatefulWidget {
  const NotificacionesScreen({super.key});

  @override
  State<NotificacionesScreen> createState() => _NotificacionesScreenState();
}

class _NotificacionesScreenState extends State<NotificacionesScreen> {
  List<dynamic> alertas = [];
  bool loading = true;

  @override
  void initState() {
    super.initState();
    _cargar();
  }

  Future<void> _cargar() async {
    try {
      final res = await http.get(Uri.parse('$API_BASE/api/notificaciones'));
      setState(() {
        alertas = jsonDecode(res.body);
        loading = false;
      });
    } catch (e) {
      setState(() => loading = false);
    }
  }

  Color _color(String tipo) {
    if (tipo.contains('Plaga') || tipo.contains('Enfermedad')) return Colors.red;
    if (tipo.contains('Hídrico')) return Colors.orange;
    return Colors.green;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: const Color(0xFF2E7D32),
        title: const Text('Notificaciones', style: TextStyle(color: Colors.white)),
      ),
      body: loading
          ? const Center(child: CircularProgressIndicator())
          : alertas.isEmpty
              ? const Center(child: Text('Sin alertas recientes'))
              : ListView.builder(
                  padding: const EdgeInsets.all(16),
                  itemCount: alertas.length,
                  itemBuilder: (ctx, i) {
                    final a     = alertas[i];
                    final color = _color(a['tipo_alerta'] ?? '');
                    return Container(
                      margin: const EdgeInsets.only(bottom: 10),
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        color: color.withOpacity(0.15),
                        border: Border.all(color: color),
                        borderRadius: BorderRadius.circular(10),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(a['tipo_alerta'] ?? '', style: TextStyle(fontWeight: FontWeight.bold, color: color)),
                          const SizedBox(height: 4),
                          Text(a['mensaje'] ?? ''),
                          const SizedBox(height: 4),
                          Text(a['fecha_hora'] ?? '', style: const TextStyle(fontSize: 12, color: Colors.grey)),
                        ],
                      ),
                    );
                  },
                ),
    );
  }
}

// ─────────────────────────────────────────
// PANTALLA REGISTROS
// ─────────────────────────────────────────
class RegistrosScreen extends StatefulWidget {
  const RegistrosScreen({super.key});

  @override
  State<RegistrosScreen> createState() => _RegistrosScreenState();
}

class _RegistrosScreenState extends State<RegistrosScreen> {
  List<dynamic> registros = [];
  bool loading = true;

  @override
  void initState() {
    super.initState();
    _cargar();
  }

  Future<void> _cargar() async {
    try {
      final res = await http.get(Uri.parse('$API_BASE/api/registros'));
      setState(() {
        registros = jsonDecode(res.body);
        loading   = false;
      });
    } catch (e) {
      setState(() => loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: const Color(0xFF2E7D32),
        title: const Text('Registros', style: TextStyle(color: Colors.white)),
      ),
      body: loading
          ? const Center(child: CircularProgressIndicator())
          : ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: registros.length,
              itemBuilder: (ctx, i) {
                final r        = registros[i];
                final esSano   = r['resultado_ia'] == 'Café Sano';
                return Container(
                  margin: const EdgeInsets.only(bottom: 8),
                  padding: const EdgeInsets.all(14),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    border: Border.all(color: Colors.grey[300]!),
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: Row(
                    children: [
                      Icon(
                        esSano ? Icons.check_circle : Icons.warning,
                        color: esSano ? Colors.green : Colors.red,
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(r['resultado_ia'] ?? '', style: const TextStyle(fontWeight: FontWeight.bold)),
                            Text(r['fecha_hora'] ?? '', style: const TextStyle(fontSize: 12, color: Colors.grey)),
                          ],
                        ),
                      ),
                      Text(
                        '${((r['confianza_ia'] ?? 0) * 100).toStringAsFixed(0)}%',
                        style: const TextStyle(fontWeight: FontWeight.bold),
                      ),
                    ],
                  ),
                );
              },
            ),
    );
  }
}

// ─────────────────────────────────────────
// WIDGET REUTILIZABLE
// ─────────────────────────────────────────
class _Tarjeta extends StatelessWidget {
  final String titulo;
  final String contenido;
  final IconData icono;
  final Color color;

  const _Tarjeta({
    required this.titulo,
    required this.contenido,
    required this.icono,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        border: Border.all(color: Colors.grey[200]!),
        borderRadius: BorderRadius.circular(10),
        boxShadow: [BoxShadow(color: Colors.grey[100]!, blurRadius: 4)],
      ),
      child: Row(
        children: [
          Icon(icono, color: color, size: 28),
          const SizedBox(width: 12),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(titulo, style: const TextStyle(fontSize: 12, color: Colors.grey)),
              Text(contenido, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
            ],
          ),
        ],
      ),
    );
  }
}