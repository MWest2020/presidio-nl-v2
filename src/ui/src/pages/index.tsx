import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { DocumentUpload } from '../components/document-upload';
import { DocumentCard } from '../components/document-card';
import { Layout } from '../components/layout';
import { Button } from '../components/ui/button';
import type { DocumentDto } from '../types';

export default function HomePage() {
  const [documents, setDocuments] = useState<DocumentDto[]>([]);
  const navigate = useNavigate();
  
  // In a real app, we'd fetch the documents from the API
  // Since there's no endpoint for listing documents, we'll use localStorage to simulate
  useEffect(() => {
    const storedDocs = localStorage.getItem('openAnonymiser_docs');
    if (storedDocs) {
      try {
        setDocuments(JSON.parse(storedDocs));
      } catch (err) {
        console.error('Failed to parse stored documents', err);
      }
    }
  }, []);
  
  // Save documents to localStorage when they change
  useEffect(() => {
    if (documents.length > 0) {
      localStorage.setItem('openAnonymiser_docs', JSON.stringify(documents));
    }
  }, [documents]);
  
  const handleUploadSuccess = (newDocs: DocumentDto[]) => {
    setDocuments(prev => [...newDocs, ...prev]);
  };
  
  const handleViewDocument = (id: string) => {
    navigate(`/document/${id}`);
  };
  
  const handleAnonymizeDocument = (id: string) => {
    navigate(`/document/anonymize/${id}`);
  };

  return (
    <Layout>
      <div className="mb-8">
        <h2 className="text-2xl font-bold mb-4">Document Management</h2>
        <p className="text-gray-600 mb-4">
          Upload documents for anonymization or deanonymize previously processed documents.
        </p>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <DocumentUpload onUploadSuccess={handleUploadSuccess} />
          
          <div>
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-xl font-semibold">Deanonymize</h3>
              <Link to="/deanonymize">
                <Button variant="outline">Deanonymize Document</Button>
              </Link>
            </div>
            <p className="text-gray-600">
              Upload a previously anonymized document to restore the original content.
            </p>
          </div>
        </div>
      </div>
      
      <div className="mt-8">
        <h2 className="text-2xl font-bold mb-4">Your Documents</h2>
        {documents.length === 0 ? (
          <p className="text-gray-500">No documents uploaded yet. Use the form above to upload your first document.</p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {documents.map(doc => (
              <DocumentCard 
                key={doc.id}
                document={doc}
                onViewClick={handleViewDocument}
                onAnonymizeClick={handleAnonymizeDocument}
              />
            ))}
          </div>
        )}
      </div>
    </Layout>
  );
}
