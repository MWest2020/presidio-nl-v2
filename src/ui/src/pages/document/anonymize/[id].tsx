import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { AnonymizationForm } from '../../../components/anonymization-form';
import { Layout } from '../../../components/layout';
import { Button } from '../../../components/ui/button';
import { api } from '../../../lib/api';
import type { DocumentDto } from '../../../types';

export default function AnonymizePage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [document, setDocument] = useState<DocumentDto | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  useEffect(() => {
    const fetchDocument = async () => {
      if (!id) return;
      
      try {
        setLoading(true);
        const data = await api.getDocumentMetadata(id, true);
        setDocument(data);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load document');
      } finally {
        setLoading(false);
      }
    };
    
    fetchDocument();
  }, [id]);
  
  const handleBack = () => {
    navigate('/');
  };
  
  const handleComplete = () => {
    navigate('/');
  };
  
  if (loading) {
    return (
      <Layout>
        <div className="flex justify-center items-center h-32">
          Loading document...
        </div>
      </Layout>
    );
  }
  
  if (error || !document) {
    return (
      <Layout>
        <div className="mb-4">
          <Button variant="outline" onClick={handleBack}>Back to Documents</Button>
        </div>
        <div className="p-4 border border-red-300 bg-red-50 rounded-md">
          <h2 className="text-lg font-medium text-red-800 mb-2">Error</h2>
          <p>{error || 'Document not found'}</p>
        </div>
      </Layout>
    );
  }
  
  return (
    <Layout>
      <div className="mb-4">
        <Button variant="outline" onClick={handleBack}>Back to Documents</Button>
      </div>
      
      <AnonymizationForm document={document} onComplete={handleComplete} />
    </Layout>
  );
}
