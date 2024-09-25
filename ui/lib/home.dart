import 'dart:io'; // Import to handle File
import 'package:firebase_auth/firebase_auth.dart';
import 'package:firebase_ui_auth/firebase_ui_auth.dart';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:http/http.dart' as http;
import 'package:flutter/foundation.dart';
import 'dart:typed_data';
import 'package:http_parser/http_parser.dart';
import 'package:mime/mime.dart';
import 'package:file_picker/file_picker.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  _HomeScreenState createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  XFile? _pickedFile; // To store the picked image
  Uint8List? _fileBytes;
  String? _fileName;
  final user = FirebaseAuth.instance.currentUser;


  /* Function to handle image selection (modify as per your implementation)
  Future<void> _pickImage() async {
    // Your code to pick the image and set _pickedFile
    // For example, using ImagePicker:
    // final pickedFile = await ImagePicker().getImage(source: ImageSource.gallery);
    // setState(() {
    //   _pickedFile = File(pickedFile.path);
    //   _onImageSelected();
    // });

    // For demonstration, let's assume _pickedFile is set here
    setState(() {
      _pickedFile = File('path/to/your/image.png');
      _onImageSelected(); // Call the function when image is selected
    });
  }

  // Function to be called when an image is selected
  void _onImageSelected() {
    if (_pickedFile != null && !_hasSentRequest) {
      _hasSentRequest = true;
      _makeHttpRequest();
    }
  }*/

  // Function to make the HTTP request
  Future<void> _postPostImageToDB() async {
    final url = 'https://us-central1-puurlee.cloudfunctions.net/file_to_nosql'; //'http://127.0.0.1:8080';
    final userId = user!.uid;

    try {
      // Example HTTP POST request
      var request = http.MultipartRequest('POST', Uri.parse(url));
      // Check which image data is available and add it to the request
      if (_fileBytes != null) {
        // Replace with the actual file name if available
        String? mimeType = lookupMimeType(_fileName!);

        if (mimeType != null) {
          final mimeTypeData = mimeType.split('/');

          request.files.add(http.MultipartFile.fromBytes(
            'file',
            _fileBytes!,
            filename: _fileName,
            contentType: MediaType(mimeTypeData[0], mimeTypeData[1]),
          ));
        } else {
          // Handle error: could not determine MIME type
          print('Could not determine MIME type of the file.');
          return;
        }
      }  else {
        // Handle the case where no image is selected
        print('_postPostImageToDB No image selected.');
        return; // Exit the function early
      }
      request.fields['user_id'] = userId;

      var response = await request.send();

      if (response.statusCode == 200) {
        print('Image uploaded successfully.');
        // Handle success response
      } else {
        print('Image upload failed with status: ${response.statusCode}.');
        // Handle failure response
      }
    } catch (e) {
      print('An error occurred: $e');
      // Handle exception
    }
  }

  @override
  Widget build(BuildContext context) {

    // Check if displayName is null and redirect to enter name screen if necessary
    if (user != null && user?.displayName == null) {
      return EnterNameScreen();
    }

    return Scaffold(
      appBar: AppBar(
        actions: [
          IconButton(
            icon: const Icon(Icons.person),
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute<ProfileScreen>(
                  builder: (context) => const ProfileScreen(),
                ),
              );
            },
          )
        ],
        automaticallyImplyLeading: false,
      ),
      body: Center(
        child: SingleChildScrollView( // To prevent overflow when image is large
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Image.asset('assets/images/puurlee_logo.png'),
              Text(
                'Welcome ${user?.displayName ?? "You"}!',
                style: Theme.of(context).textTheme.displaySmall,
              ),
              const SizedBox(height: 20),
              _pickedFile != null || _fileBytes != null
                  ? kIsWeb
                    ? Image.memory(_fileBytes!)
                    : Image.file(File(_pickedFile!.path))
                  : const Text('No image selected.'),
            ],
          ),
        ),
      ),
      // Floating action button to open the camera
      floatingActionButton: FloatingActionButton(
        onPressed: _openCamera,
        child: const Icon(Icons.camera_alt),
      ),
    );
  }

  // Function to open the camera using image_picker
  Future<void> _openCamera() async {
    final picker = ImagePicker();
    try {
      if (!kIsWeb){
        _pickedFile = await picker.pickImage(source: ImageSource.camera);
        _fileBytes = await _pickedFile!.readAsBytes();
        _fileName = _pickedFile!.name;
      } else {
        final allowedExtensions = ['jpg', 'jpeg', 'png', 'pdf'];

        // Open the file picker
        FilePickerResult? result = await FilePicker.platform.pickFiles(
          type: FileType.custom,
          allowedExtensions: allowedExtensions,
        );

        if (result != null) {
          _fileBytes = result.files.first.bytes;
          _fileName = result.files.first.name;
        }
      }

      _postPostImageToDB();
      setState(() {
        // Update the UI
      });

    } catch (e) {
      print('Error picking image: $e');
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error opening camera: $e')),
      );
    }
  }
}

class EnterNameScreen extends StatefulWidget {
  @override
  _EnterNameScreenState createState() => _EnterNameScreenState();
}

class _EnterNameScreenState extends State<EnterNameScreen> {
  final _formKey = GlobalKey<FormState>();
  final _firstNameController = TextEditingController();
  final _lastNameController = TextEditingController();

  @override
  void dispose() {
    _firstNameController.dispose();
    _lastNameController.dispose();
    super.dispose();
  }

  Future<void> _updateDisplayName() async {
    final user = FirebaseAuth.instance.currentUser;
    if (user != null) {
      String fullName =
          '${_firstNameController.text} ${_lastNameController.text}';

      try {
        await user.updateDisplayName(fullName);
        await user.reload(); // Reload to make the changes effective

        // Navigate back to the home screen after update
        Navigator.of(context).pushReplacement(
          MaterialPageRoute(builder: (context) => const HomeScreen()),
        );
      } catch (e) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error updating display name: $e')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Enter Your Name')),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Form(
          key: _formKey,
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              TextFormField(
                controller: _firstNameController,
                decoration: const InputDecoration(labelText: 'First Name'),
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return 'Please enter your first name';
                  }
                  return null;
                },
              ),
              TextFormField(
                controller: _lastNameController,
                decoration: const InputDecoration(labelText: 'Last Name'),
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return 'Please enter your last name';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 20),
              ElevatedButton(
                onPressed: () {
                  if (_formKey.currentState!.validate()) {
                    _updateDisplayName(); // Update displayName in Firebase
                  }
                },
                child: const Text('Submit'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
