import React, { useState } from 'react';
import { StyleSheet, View, TouchableOpacity, Text, Alert } from 'react-native';
import * as DocumentPicker from 'expo-document-picker';
import axios from 'axios';

export default function App() {
  const [isUploading, setIsUploading] = useState(false);

  const handleUpload = async () => {
    try {
      const result = await DocumentPicker.getDocumentAsync({
        type: 'application/pdf',
      });

      if (result.type === 'success') {
        setIsUploading(true);
        
        // Create form data
        const formData = new FormData();
        formData.append('file', {
          uri: result.uri,
          type: 'application/pdf',
          name: result.name,
        });

        // Upload to backend
        const response = await axios.post('http://localhost:8000/upload', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });

        Alert.alert('Success', 'File processed successfully!', [
          { text: 'OK', onPress: () => console.log(response.data) },
        ]);
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to upload file');
      console.error(error);
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <View style={styles.container}>
      <TouchableOpacity
        style={styles.uploadButton}
        onPress={handleUpload}
        disabled={isUploading}
      >
        <Text style={styles.buttonText}>
          {isUploading ? 'Processing...' : 'Upload PDF'}
        </Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
    alignItems: 'center',
    justifyContent: 'center',
  },
  uploadButton: {
    backgroundColor: '#007AFF',
    padding: 20,
    borderRadius: 10,
  },
  buttonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
}); 