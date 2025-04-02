
import FileUpload from '@/components/FileUpload';

export default function UploadPage() {
  return (
    <main className="min-h-screen p-8 max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold mb-8">Document Upload</h1>
      <FileUpload />
    </main>
  );
}
