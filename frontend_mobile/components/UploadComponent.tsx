import React, { useState } from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import * as DocumentPicker from 'expo-document-picker';
import axios from 'axios';

// Update this to your laptop's IP address
const API_BASE_URL = 'http://10.25.49.236:8000';

export const UploadComponent = () => {
  const [uploadStatus, setUploadStatus] = useState('');
  const [error, setError] = useState('');

  const handleUpload = async () => {
    try {
      setUploadStatus('Selecting file...');
      setError('');

      // Pick a document
      const result = await DocumentPicker.getDocumentAsync({
        type: '*/*', // Accept all file types
        copyToCacheDirectory: true,
      });

      if (result.type === 'success') {
        setUploadStatus('Uploading...');

        // Create form data
        const formData = new FormData();
        formData.append('files', {
          uri: result.uri,
          type: result.mimeType,
          name: result.name,
        } as any);

        console.log('Uploading to:', `${API_BASE_URL}/upload/upload`);

        // Upload the file
        const response = await axios.post(`${API_BASE_URL}/upload/upload`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });

        if (response.status === 200) {
          setUploadStatus('Upload successful!');
          console.log('Upload response:', response.data);
        }
      }
    } catch (error) {
      console.error('Upload error:', error);
      setError(error.response?.data?.detail || 'Failed to upload file');
      setUploadStatus('');
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Upload Files</Text>
      
      <TouchableOpacity
        style={styles.uploadButton}
        onPress={handleUpload}
      >
        <Text style={styles.buttonText}>Select and Upload File</Text>
      </TouchableOpacity>

      {uploadStatus ? (
        <Text style={styles.status}>{uploadStatus}</Text>
      ) : null}

      {error ? (
        <Text style={styles.error}>{error}</Text>
      ) : null}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    padding: 20,
    backgroundColor: '#f9f9f9',
    borderRadius: 8,
    margin: 10,
  },
  title: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 20,
    textAlign: 'center',
  },
  uploadButton: {
    backgroundColor: '#007bff',
    padding: 15,
    borderRadius: 4,
    alignItems: 'center',
  },
  buttonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
  status: {
    color: '#28a745',
    marginTop: 10,
    textAlign: 'center',
  },
  error: {
    color: '#dc3545',
    marginTop: 10,
    textAlign: 'center',
  },
}); 