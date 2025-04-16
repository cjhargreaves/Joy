import React, { useEffect, useState } from 'react';
import { View, Text, ScrollView, StyleSheet, ActivityIndicator, TouchableOpacity } from 'react-native';
import { useLocalSearchParams } from 'expo-router';
import axios from 'axios';

export default function Results() {
  const { resultId, apiBaseUrl } = useLocalSearchParams();
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [pollCount, setPollCount] = useState(0);
  const [expandedSections, setExpandedSections] = useState({});

  // Poll for results
  useEffect(() => {
    const pollInterval = setInterval(async () => {
      if (!resultId || !apiBaseUrl) {
        clearInterval(pollInterval);
        setError("Missing result ID or API base URL");
        setLoading(false);
        return;
      }

      try {
        console.log(`Polling for results (attempt ${pollCount + 1})...`);
        const response = await axios.get(`${apiBaseUrl}/status/${resultId}`);
        console.log('Poll response:', response.data);
        
        setResult(response.data);
        
        // If processing is complete or error, stop polling
        if (response.data.status === 'completed' || response.data.status === 'error') {
          clearInterval(pollInterval);
          setLoading(false);
        }
        
        setPollCount(count => count + 1);
        
        // Stop polling after 30 attempts (5 minutes)
        if (pollCount >= 30) {
          clearInterval(pollInterval);
          setError("Processing timeout. Please try again.");
          setLoading(false);
        }
      } catch (err) {
        console.error('Error polling for results:', err);
        // Don't stop polling on error, just log it
      }
    }, 10000); // Poll every 10 seconds
    
    // Initial poll
    pollForResults();

    return () => clearInterval(pollInterval);
  }, [resultId, apiBaseUrl, pollCount]);

  // Initial poll function
  const pollForResults = async () => {
    if (!resultId || !apiBaseUrl) {
      setError("Missing result ID or API base URL");
      setLoading(false);
      return;
    }

    try {
      console.log('Initial poll for results...');
      const response = await axios.get(`${apiBaseUrl}/status/${resultId}`);
      console.log('Initial poll response:', response.data);
      
      setResult(response.data);
      
      // If processing is complete, stop loading
      if (response.data.status === 'completed' || response.data.status === 'error') {
        setLoading(false);
      }
    } catch (err) {
      console.error('Error on initial poll for results:', err);
      // Continue polling even if initial poll fails
    }
  };

  // Helper function to render a value
  const renderValue = (value) => {
    if (value === null || value === undefined) return <Text style={styles.nullValue}>Not Available</Text>;
    if (Array.isArray(value)) {
      return value.map((item, index) => (
        <Text key={index} style={styles.arrayItem}>• {JSON.stringify(item)}</Text>
      ));
    }
    if (typeof value === 'object') {
      return Object.entries(value).map(([key, val]) => (
        <View key={key} style={styles.nestedRow}>
          <Text style={styles.nestedLabel}>{key.replace(/_/g, ' ')}:</Text>
          <Text style={styles.nestedValue}>{JSON.stringify(val)}</Text>
        </View>
      ));
    }
    return <Text style={styles.value}>{value}</Text>;
  };

  // Helper function to render sections
  const renderSection = (title, content, sectionKey) => {
    if (!content) return null;
    
    const isExpanded = expandedSections[sectionKey];
    
    return (
      <TouchableOpacity 
        style={styles.section}
        onPress={() => setExpandedSections(prev => ({...prev, [sectionKey]: !prev[sectionKey]}))}
      >
        <View style={styles.sectionHeader}>
          <Text style={styles.sectionTitle}>{title}</Text>
          <Text style={styles.expandButton}>{isExpanded ? '▼' : '▶'}</Text>
        </View>
        
        {isExpanded && (
          <View style={styles.sectionContent}>
            {Object.entries(content).map(([key, value]) => (
              <View key={key} style={styles.row}>
                <Text style={styles.label}>
                  {key.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}:
                </Text>
                {renderValue(value)}
              </View>
            ))}
          </View>
        )}
      </TouchableOpacity>
    );
  };

  // Display loading state
  if (loading || !result || result.status === 'processing') {
    return (
      <View style={[styles.container, styles.centered]}>
        <ActivityIndicator size="large" color="#0000ff" />
        <Text style={styles.loadingText}>
          Processing document... This may take a minute.
        </Text>
        <Text style={styles.subText}>
          We're using AI to analyze your medical document.
        </Text>
      </View>
    );
  }

  // Display error state
  if (error || result.status === 'error') {
    return (
      <View style={[styles.container, styles.centered]}>
        <Text style={styles.errorText}>Error: {error || result.error}</Text>
        <Text style={styles.subText}>Please try scanning your document again.</Text>
      </View>
    );
  }

  const { analysis } = result;

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>EMR Analysis Results</Text>
      
      {/* Core Patient Information */}
      {renderSection('Core Patient Information', analysis?.core_patient_information, 'core')}
      
      {/* Clinical Data */}
      {renderSection('Clinical Data', analysis?.clinical_data, 'clinical')}
      
      {/* Visit Information */}
      {renderSection('Visit Information', analysis?.visit_information, 'visit')}
      
      {/* Administrative */}
      {renderSection('Administrative', analysis?.administrative, 'admin')}
      
      {/* Metadata */}
      {renderSection('Document Metadata', analysis?.metadata, 'metadata')}
      
      {/* Raw OCR Data Section */}
      <TouchableOpacity 
        style={styles.section}
        onPress={() => setExpandedSections(prev => ({...prev, raw: !prev.raw}))}
      >
        <View style={styles.sectionHeader}>
          <Text style={styles.sectionTitle}>Raw OCR Data</Text>
          <Text style={styles.expandButton}>{expandedSections.raw ? '▼' : '▶'}</Text>
        </View>
        {expandedSections.raw && (
          <View style={styles.sectionContent}>
            <Text style={styles.rawText}>{result.ocr_data?.raw_text || 'No raw text available'}</Text>
          </View>
        )}
      </TouchableOpacity>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
    padding: 16,
  },
  centered: {
    justifyContent: 'center',
    alignItems: 'center',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 20,
    textAlign: 'center',
    color: '#2c3e50',
  },
  section: {
    backgroundColor: 'white',
    borderRadius: 10,
    padding: 16,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#34495e',
  },
  expandButton: {
    fontSize: 18,
    color: '#7f8c8d',
  },
  sectionContent: {
    marginTop: 12,
  },
  row: {
    marginBottom: 12,
  },
  label: {
    fontSize: 14,
    fontWeight: '600',
    color: '#7f8c8d',
    marginBottom: 4,
  },
  value: {
    fontSize: 14,
    color: '#2c3e50',
  },
  nullValue: {
    fontSize: 14,
    color: '#95a5a6',
    fontStyle: 'italic',
  },
  arrayItem: {
    fontSize: 14,
    color: '#2c3e50',
    marginLeft: 8,
    marginBottom: 2,
  },
  nestedRow: {
    marginLeft: 8,
    marginBottom: 2,
  },
  nestedLabel: {
    fontSize: 13,
    color: '#7f8c8d',
    fontWeight: '500',
  },
  nestedValue: {
    fontSize: 13,
    color: '#2c3e50',
  },
  rawText: {
    fontSize: 14,
    color: '#2c3e50',
    fontFamily: 'monospace',
  },
  loadingText: {
    marginTop: 20,
    fontSize: 18,
    color: '#444',
    fontWeight: '600',
    textAlign: 'center',
  },
  subText: {
    marginTop: 10,
    fontSize: 14,
    color: '#666',
    textAlign: 'center',
    paddingHorizontal: 30,
  },
  errorText: {
    fontSize: 18,
    color: '#e74c3c',
    fontWeight: 'bold',
    textAlign: 'center',
  },
}); 