import 'package:flutter/material.dart';

void main() {
  runApp(PlantHealthApp());
}

class PlantHealthApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Plant Health',
      theme: ThemeData.dark(),
      home: PlantForm(),
    );
  }
}

class PlantForm extends StatefulWidget {
  @override
  _PlantFormState createState() => _PlantFormState();
}

class _PlantFormState extends State<PlantForm> {
  final _formKey = GlobalKey<FormState>();
  String species = '';
  String sampleName = '';
  double fvfm = 0.75;
  double spad = 30.0;
  double chlTot = 1.5;
  double carTot = 1.0;
  double qp = 0.6;
  double qn = 0.4;

  void _resetForm() {
    setState(() {
      species = '';
      sampleName = '';
      fvfm = 0.75;
      spad = 30.0;
      chlTot = 1.5;
      carTot = 1.0;
      qp = 0.6;
      qn = 0.4;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('🌿 Plant Health Mobile'),
            Text(
              'Developed by Giuseppe Muscari Tomajoli ©2025',
              style: TextStyle(fontSize: 12, color: Colors.grey[400]),
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: Icon(Icons.refresh),
            tooltip: 'Reset form',
            onPressed: _resetForm,
          ),
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Form(
          key: _formKey,
          child: ListView(
            children: [
              TextFormField(
                decoration: InputDecoration(labelText: 'Species'),
                onChanged: (val) => species = val,
              ),
              TextFormField(
                decoration: InputDecoration(labelText: 'Sample Name'),
                onChanged: (val) => sampleName = val,
              ),
              SizedBox(height: 20),
              _buildSlider('Fv/Fm', fvfm, 0.0, 1.0, (val) => setState(() => fvfm = val)),
              _buildSlider('SPAD', spad, 0.0, 60.0, (val) => setState(() => spad = val)),
              _buildSlider('Chl TOT', chlTot, 0.0, 5.0, (val) => setState(() => chlTot = val)),
              _buildSlider('CAR TOT', carTot, 0.0, 5.0, (val) => setState(() => carTot = val)),
              _buildSlider('qp', qp, 0.0, 1.0, (val) => setState(() => qp = val)),
              _buildSlider('qN', qn, 0.0, 1.0, (val) => setState(() => qn = val)),
              SizedBox(height: 20),
              ElevatedButton(
                onPressed: () {
                  String health = _evaluateHealth(fvfm, spad, chlTot, carTot, qp, qn);
                  showDialog(
                    context: context,
                    builder: (_) => AlertDialog(
                      title: Text('📋 Results'),
                      content: Text(
                        'Species: $species\n'
                        'Sample: $sampleName\n'
                        'Fv/Fm: ${fvfm.toStringAsFixed(2)}\n'
                        'SPAD: ${spad.toStringAsFixed(1)}\n'
                        'Chl TOT: ${chlTot.toStringAsFixed(1)}\n'
                        'CAR TOT: ${carTot.toStringAsFixed(1)}\n'
                        'qp: ${qp.toStringAsFixed(2)}\n'
                        'qN: ${qn.toStringAsFixed(2)}\n\n'
                        '🧬 Health Status: $health',
                      ),
                    ),
                  );
                },
                child: Text('Evaluate Health'),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildSlider(String label, double value, double min, double max, ValueChanged<double> onChanged) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('$label: ${value.toStringAsFixed(2)}'),
        Slider(
          value: value,
          min: min,
          max: max,
          divisions: 100,
          onChanged: onChanged,
        ),
      ],
    );
  }

  String _evaluateHealth(double fvfm, double spad, double chlTot, double carTot, double qp, double qn) {
    if (fvfm < 0.6 || spad < 20 || chlTot < 1.0 || carTot < 1.0 || qp < 0.4 || qn > 0.6) {
      return '❌ High Stress';
    } else if (fvfm < 0.75 || spad < 30 || chlTot < 2.0 || carTot < 2.0 || qp < 0.6 || qn > 0.5) {
      return '⚠️ Moderate Stress';
    } else {
      return '✅ Healthy';
    }
  }
}
