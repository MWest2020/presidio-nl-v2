import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { formatDate, groupPiiEntitiesByType } from '../lib/utils';
import type { DocumentDto } from '../types';

interface DocumentViewerProps {
  document: DocumentDto;
  onAnonymizeClick: (id: string) => void;
  onViewDetailsClick?: (id: string) => void;
}

export function DocumentViewer({ document, onAnonymizeClick, onViewDetailsClick }: DocumentViewerProps) {

  const piiGroups = groupPiiEntitiesByType(document.pii_entities);
  
  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2">
          <span className="break-words">{document.filename}</span>
          <Badge className="whitespace-nowrap">{document.content_type}</Badge>
        </CardTitle>
        <p className="text-xs sm:text-sm text-gray-500">Uploaded: {formatDate(document.uploaded_at)}</p>
      </CardHeader>
      <CardContent className="space-y-3 sm:space-y-4">
        <div>
          <h3 className="text-base sm:text-lg font-medium mb-1 sm:mb-2">Document Details</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-1 sm:gap-2 text-xs sm:text-sm">
            <span className="font-medium">ID:</span>
            <span className="font-mono break-all">{document.id}</span>
          </div>
        </div>
        
        {document.tags.length > 0 && (
          <div>
            <h3 className="text-base sm:text-lg font-medium mb-1 sm:mb-2">Tags</h3>
            <div className="flex flex-wrap gap-1">
              {document.tags.map(tag => (
                <Badge key={tag.id} variant="secondary" className="text-xs">{tag.name}</Badge>
              ))}
            </div>
          </div>
        )}
        
        <div>
          <h3 className="text-base sm:text-lg font-medium mb-1 sm:mb-2">Detected PII Entities</h3>
          {document.pii_entities.length === 0 ? (
            <p className="text-gray-500 text-xs sm:text-sm">No PII entities detected</p>
          ) : (
            <div className="space-y-3 sm:space-y-4 overflow-x-auto">
              {Object.entries(piiGroups).map(([type, entities]) => (
                <div key={type} className="border-b pb-2">
                  <h4 className="font-medium mb-1 text-sm sm:text-base">{type}</h4>
                  <ul className="list-disc list-inside space-y-1">
                    {entities.map((entity, idx) => (
                      <li key={idx} className="text-xs sm:text-sm break-words">
                        {entity.text}
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          )}
        </div>
        
        <div className="flex justify-end mt-3 sm:mt-4 gap-2">
          {onViewDetailsClick && (
            <Button 
              onClick={() => onViewDetailsClick(document.id)} 
              variant="outline" 
              className="w-full sm:w-auto"
            >
              View Details
            </Button>
          )}
          <Button onClick={() => onAnonymizeClick(document.id)} className="w-full sm:w-auto">
            Anonymize Document
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
