'use client';

import { useState, useCallback, useEffect } from 'react';
import { useDropzone } from 'react-dropzone';

export default function FileUpload() {
  const [files, setFiles] = useState<File[]>([]);
  const [uploading, setUploading] = useState(false);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    setFiles(acceptedFiles);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
    },
    multiple: true
  });

  const handleUpload = async () => {
    if (files.length === 0) {
      alert('Please select a file first');
      return;
    }

    try {
      setUploading(true);
      console.log('Starting upload for file:', files[0].name);

      const formData = new FormData();
      files.forEach((file) => {
        formData.append('files', file);
      });
      const response = await fetch('http://127.0.0.1:8000/upload/', {
        method: 'POST',
        body: formData,
      });

      console.log('Response status:', response.status);
      const data = await response.json();
      console.log('Response data:', data);

      if (!response.ok) {
        throw new Error(`Upload failed: ${data.message || response.statusText}`);
      }


      setFiles([]);
      alert('Upload successful!');
    } catch (error) {
      console.error('Upload error:', error);
      alert(`Upload failed: ${error.message}`);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="w-full">
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors
          ${isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'}`}
      >
        <input {...getInputProps()} />
        {isDragActive ? (
          <p className="text-blue-500">Drop the file here...</p>
        ) : (
          <div>
            <p className="mb-2">Drag & drop a file here, or click to select</p>
            <p className="text-sm text-gray-500">Supported formats: PDF, DOC, DOCX</p>
          </div>
        )}
      </div>

      {files.length > 0 && (
        <div className="mt-4">
          <div className="mb-3">
            <p className="text-sm font-medium text-gray-700">Selected files:</p>
            <ul className="mt-1 text-sm text-gray-500">
              {files.map((file, index) => (
                <li key={index} className="flex items-center">
                  <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  {file.name}
                </li>
              ))}
            </ul>
          </div>
          <button
            onClick={handleUpload}
            disabled={uploading}
            className="w-full px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:bg-blue-300 disabled:cursor-not-allowed"
          >
            {uploading ? `Uploading ${files.length} files...` : `Upload ${files.length} Files`}
          </button>
        </div>
      )}
    </div>
  );
}

