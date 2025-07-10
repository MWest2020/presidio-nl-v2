import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { formatDate, groupPiiEntitiesByType } from '../lib/utils';
import { api } from '../lib/api';
import type { DocumentDto } from '../types';

interface DocumentViewerProps {
  documentId: string;
  onAnonymizeClick: (id: string) => void;
}

export function DocumentViewer({ documentId, onAnonymizeClick }: DocumentViewerProps) {
  const [document, setDocument] = useState<DocumentDto | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  useEffect(() => {
    const fetchDocument = async () => {
      try {
        setLoading(true);
        const data = await api.getDocumentMetadata(documentId, true);
        setDocument(data);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load document');
      } finally {
        setLoading(false);
      }
    };
    
    fetchDocument();
  }, [documentId]);
  
  if (loading) {
    return <div className="flex justify-center p-8">Loading document...</div>;
  }
  
  if (error) {
    return <div className="text-red-500 p-4 border border-red-300 rounded-md">{error}</div>;
  }
  
  if (!document) {
    return <div>Document not found</div>;
  }

  const piiGroups = groupPiiEntitiesByType(document.pii_entities);
  
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex justify-between items-center">
          <span>{document.filename}</span>
          <Badge>{document.content_type}</Badge>
        </CardTitle>
        <p className="text-sm text-gray-500">Uploaded: {formatDate(document.uploaded_at)}</p>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <h3 className="text-lg font-medium mb-2">Document Details</h3>
          <div className="grid grid-cols-2 gap-2 text-sm">
            <span className="font-medium">ID:</span>
            <span className="font-mono">{document.id}</span>
          </div>
        </div>
        
        {document.tags.length > 0 && (
          <div>
            <h3 className="text-lg font-medium mb-2">Tags</h3>
            <div className="flex flex-wrap gap-1">
              {document.tags.map(tag => (
                <Badge key={tag.id} variant="secondary">{tag.name}</Badge>
              ))}
            </div>
          </div>
        )}
        
        <div>
          <h3 className="text-lg font-medium mb-2">Detected PII Entities</h3>
          {document.pii_entities.length === 0 ? (
            <p className="text-gray-500">No PII entities detected</p>
          ) : (
            <div className="space-y-4">
              {Object.entries(piiGroups).map(([type, entities]) => (
                <div key={type} className="border-b pb-2">
                  <h4 className="font-medium mb-1">{type}</h4>
                  <ul className="list-disc list-inside space-y-1">
                    {entities.map((entity, idx) => (
                      <li key={idx} className="text-sm">
                        {entity.text}
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          )}
        </div>
        
        <div className="flex justify-end mt-4">
          <Button onClick={() => onAnonymizeClick(document.id)}>
            Anonymize Document
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
