
import Link from 'next/link';

export default function Home() {
  return (
    <main className="min-h-screen p-8">
      <h1 className="text-2xl font-bold mb-4">Welcome to Nurse Joy</h1>
      <Link 
        href="/upload" 
        className="text-blue-600 hover:text-blue-800 underline"
      >
        Proceed to Document Upload Page 
      </Link>
    </main>
  );
}

