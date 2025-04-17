import React, { useState, useRef } from 'react';
import { StyleSheet, View, TouchableOpacity, Text, Alert, ActivityIndicator, Image } from 'react-native';
import { CameraView, useCameraPermissions } from 'expo-camera';
import axios from 'axios';
import { router } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';

// Update this with your computer's local IP address
const API_BASE_URL = 'http://172.16.86.18:8000';

export default function Home() {
  const [isUploading, setIsUploading] = useState(false);
  const [image, setImage] = useState(null);
  const [permission, requestPermission] = useCameraPermissions();
  const cameraRef = useRef(null);
  const [uploadStatus, setUploadStatus] = useState('');

  if (!permission) {
    return <View style={styles.container}><Text>Loading...</Text></View>;
  }

  if (!permission.granted) {
    return (
      <View style={styles.container}>
        <Text style={styles.message}>We need your permission to show the camera</Text>
        <TouchableOpacity style={styles.button} onPress={requestPermission}>
          <Text style={styles.buttonText}>Grant Permission</Text>
        </TouchableOpacity>
      </View>
    );
  }

  const takePicture = async () => {
    if (cameraRef.current) {
      try {
        const photo = await cameraRef.current.takePictureAsync({
          quality: 1,
          base64: true,
          skipProcessing: true,
        });
        setImage(photo.uri);
        await handleUpload(photo.uri);
      } catch (error) {
        Alert.alert('Error', 'Failed to take picture');
      }
    }
  };

  const handleUpload = async (imageUri) => {
    try {
      setIsUploading(true);
      
      // Create form data with the correct field name
      const formData = new FormData();
      
      // Get the filename from the URI
      const filename = imageUri.split('/').pop() || 'document.jpg';
      
      // Append the file with the correct field name 'files'
      formData.append('files', {
        uri: imageUri,
        type: 'image/jpeg',
        name: filename
      });

      console.log('Starting upload...');
      console.log('Image URI:', imageUri);
      console.log('Uploading to:', `${API_BASE_URL}/upload`);
      console.log('File name:', filename);
      
      const uploadResponse = await axios.post(`${API_BASE_URL}/upload`, formData, {
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'multipart/form-data',
        },
        maxContentLength: Infinity,
        maxBodyLength: Infinity,
        timeout: 60000, // Increased to 60 seconds
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          console.log(`Upload progress: ${percentCompleted}%`);
          setUploadStatus(`Uploading: ${percentCompleted}%`);
        },
      });

      console.log('Upload response:', uploadResponse.data);
      
      if (uploadResponse.data.files && uploadResponse.data.files.length > 0) {
        Alert.alert('Success', 'File uploaded successfully!');
        setImage(null); // Reset the image
      } else {
        throw new Error('No files were uploaded');
      }
      
    } catch (error) {
      console.error('Upload error details:', {
        message: error.message,
        response: error.response?.data,
        status: error.response?.status,
        code: error.code,
        stack: error.stack
      });
      
      let errorMessage = 'Failed to upload image. ';
      if (error.response?.data?.detail) {
        errorMessage += error.response.data.detail;
      } else if (error.message.includes('Network Error') || error.code === 'ECONNABORTED') {
        errorMessage += 'Network error - please check your connection and ensure the server is running.';
      } else {
        errorMessage += error.message;
      }
      
      Alert.alert(
        'Upload Error',
        `${errorMessage}\n\nPlease make sure your laptop is running the server at ${API_BASE_URL} and both devices are on the same network.`
      );
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <View style={styles.container}>
      {!image ? (
        <CameraView
          ref={cameraRef}
          style={styles.camera}
          facing="back"
        >
          <View style={styles.overlay}>
            <Text style={styles.title}>Upload fax to send to EMR</Text>
            <TouchableOpacity
              style={styles.captureButton}
              onPress={takePicture}
              disabled={isUploading}
            >
              <Ionicons name="add-circle" size={80} color="white" />
            </TouchableOpacity>
          </View>
        </CameraView>
      ) : (
        <View style={styles.previewContainer}>
          <Image source={{ uri: image }} style={styles.previewImage} />
          <View style={styles.buttonContainer}>
            <TouchableOpacity
              style={[styles.button, styles.retakeButton]}
              onPress={() => setImage(null)}
            >
              <Text style={styles.buttonText}>Retake</Text>
            </TouchableOpacity>
          </View>
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#000',
  },
  camera: {
    flex: 1,
  },
  overlay: {
    flex: 1,
    backgroundColor: 'transparent',
    justifyContent: 'center',
    alignItems: 'center',
  },
  title: {
    color: 'white',
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 20,
    textAlign: 'center',
  },
  previewContainer: {
    flex: 1,
    backgroundColor: '#000',
    justifyContent: 'center',
    alignItems: 'center',
  },
  previewImage: {
    width: '100%',
    height: '80%',
    resizeMode: 'contain',
  },
  buttonContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    width: '100%',
    padding: 20,
  },
  button: {
    padding: 15,
    borderRadius: 10,
    alignItems: 'center',
    minWidth: 120,
  },
  captureButton: {
    width: 100,
    height: 100,
    borderRadius: 50,
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  retakeButton: {
    backgroundColor: '#f44336',
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  message: {
    color: '#fff',
    fontSize: 18,
    textAlign: 'center',
    marginBottom: 20,
  },
});
