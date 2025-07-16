import { useState, useEffect } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { DocumentViewer } from '../../components/document-viewer';
import { Layout } from '../../components/layout';
import { Button } from '../../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Badge } from '../../components/ui/badge';
import { api } from '../../lib/api';
import { formatDate, groupPiiEntitiesByType } from '../../lib/utils';
import type { DocumentDto } from '../../types';

export default function DocumentPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const location = useLocation();
  const [document, setDocument] = useState<DocumentDto | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Check if we're in detailed view mode
  const searchParams = new URLSearchParams(location.search);
  const isDetailedView = searchParams.get('view') === 'details';
  
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
  
  const handleAnonymizeClick = (documentId: string) => {
    navigate(`/document/anonymize/${documentId}`);
  };
  
  const handleViewDetailsClick = (documentId: string) => {
    // Navigate to the same URL to prevent loading a new page,
    // but add a query parameter to indicate showing detailed view
    navigate(`/document/${documentId}?view=details`);
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
  
  // Render document details view if view=details query parameter is present
  if (isDetailedView) {
    const piiGroups = groupPiiEntitiesByType(document.pii_entities);
    
    return (
      <Layout>
        <div className="mb-4">
          <Button 
            variant="outline" 
            onClick={() => navigate(`/document/${document.id}`)}
          >
            Back to Document
          </Button>
        </div>
        
        <Card className="w-full">
          <CardHeader>
            <CardTitle className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2">
              <span className="break-words">{document.filename}</span>
              <Badge className="whitespace-nowrap">{document.content_type}</Badge>
            </CardTitle>
            <p className="text-xs sm:text-sm text-gray-500">Uploaded: {formatDate(document.uploaded_at)}</p>
          </CardHeader>
          
          <CardContent>
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-medium mb-2">Document Metadata</h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 p-3 bg-gray-50 rounded-md">
                  <div>
                    <p className="text-sm font-medium text-gray-600">Document ID</p>
                    <p className="font-mono text-xs break-all">{document.id}</p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-600">Filename</p>
                    <p className="text-xs">{document.filename}</p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-600">Content Type</p>
                    <p className="text-xs">{document.content_type}</p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-600">Uploaded At</p>
                    <p className="text-xs">{formatDate(document.uploaded_at)}</p>
                  </div>
                  <div className="sm:col-span-2">
                    <p className="text-sm font-medium text-gray-600">PII Entities Count</p>
                    <p className="text-xs">{document.pii_entities.length} entities detected</p>
                  </div>
                </div>
              </div>
              
              {document.tags.length > 0 && (
                <div>
                  <h3 className="text-lg font-medium mb-2">Document Tags</h3>
                  <div className="flex flex-wrap gap-2">
                    {document.tags.map(tag => (
                      <Badge key={tag.id} variant="secondary" className="px-3 py-1 text-sm">
                        {tag.name}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}
              
              <div>
                <h3 className="text-lg font-medium mb-2">Detected PII Entities</h3>
                {document.pii_entities.length === 0 ? (
                  <p className="text-gray-500 text-sm">No PII entities detected</p>
                ) : (
                  <div className="space-y-4 overflow-x-auto">
                    {Object.entries(piiGroups).map(([type, entities]) => (
                      <div key={type} className="border rounded-md p-3">
                        <h4 className="font-medium text-base mb-2">{type}</h4>
                        <table className="w-full text-sm">
                          <thead className="bg-gray-50">
                            <tr>
                              <th className="text-left p-2">Text</th>
                              <th className="text-left p-2">Position</th>
                              <th className="text-left p-2">Confidence</th>
                            </tr>
                          </thead>
                          <tbody>
                            {entities.map((entity, idx) => (
                              <tr key={idx} className="border-t">
                                <td className="p-2 font-mono text-xs break-all">{entity.text}</td>
                                <td className="p-2 text-xs">{entity.start}-{entity.end}</td>
                                <td className="p-2 text-xs">
                                  {entity.score !== undefined ? 
                                    `${(entity.score * 100).toFixed(1)}%` : 
                                    'N/A'}
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    ))}
                  </div>
                )}
              </div>
              
              <div className="flex justify-end mt-3 sm:mt-4">
                <Button 
                  onClick={() => navigate(`/document/anonymize/${document.id}`)}
                  className="w-full sm:w-auto"
                >
                  Anonymize Document
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </Layout>
    );
  }
  
  // Regular document view
  return (
    <Layout>
      <div className="mb-4">
        <Button variant="outline" onClick={handleBack}>Back to Documents</Button>
      </div>
      
      <DocumentViewer 
        document={document}
        onAnonymizeClick={handleAnonymizeClick}
        onViewDetailsClick={handleViewDetailsClick}
      />
    </Layout>
  );
}
