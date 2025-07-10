import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Checkbox } from './ui/checkbox';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { groupPiiEntitiesByType } from '../lib/utils';
import { api } from '../lib/api';
import { downloadBlob } from '../lib/utils';
import type { DocumentDto, PiiEntityDto } from '../types';

interface AnonymizationFormProps {
  document: DocumentDto;
  onComplete: () => void;
}

export function AnonymizationForm({ document, onComplete }: AnonymizationFormProps) {
  const [selectedEntities, setSelectedEntities] = useState<PiiEntityDto[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [anonymizationResult, setAnonymizationResult] = useState<{
    status: string;
    time_taken: number;
  } | null>(null);
  
  const piiGroups = groupPiiEntitiesByType(document.pii_entities);
  
  const handleCheck = (entity: PiiEntityDto) => {
    if (selectedEntities.some(e => e.text === entity.text && e.entity_type === entity.entity_type)) {
      setSelectedEntities(selectedEntities.filter(
        e => !(e.text === entity.text && e.entity_type === entity.entity_type)
      ));
    } else {
      setSelectedEntities([...selectedEntities, entity]);
    }
  };
  
  const isSelected = (entity: PiiEntityDto) => {
    return selectedEntities.some(
      e => e.text === entity.text && e.entity_type === entity.entity_type
    );
  };
  
  const handleAnonymize = async () => {
    if (selectedEntities.length === 0) {
      setError('Please select at least one entity to anonymize');
      return;
    }
    
    setIsProcessing(true);
    setError(null);
    
    try {
      const result = await api.anonymizeDocument(document.id, selectedEntities);
      setAnonymizationResult({
        status: result.status,
        time_taken: result.time_taken
      });
      setSuccess(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Anonymization failed');
    } finally {
      setIsProcessing(false);
    }
  };
  
  const handleDownload = async () => {
    try {
      window.location.href = api.getDocumentDownloadUrl(document.id);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Download failed');
    }
  };
  
  return (
    <Card>
      <CardHeader>
        <CardTitle>Anonymize Document: {document.filename}</CardTitle>
      </CardHeader>
      <CardContent>
        {success ? (
          <div className="space-y-4">
            <div className="p-4 border border-green-200 bg-green-50 rounded-md">
              <h3 className="font-medium text-green-800">Anonymization Complete</h3>
              <p>Status: {anonymizationResult?.status}</p>
              <p>Time taken: {anonymizationResult?.time_taken}ms</p>
            </div>
            
            <div className="space-y-2">
              <h4 className="font-medium">Anonymized Entities:</h4>
              <div className="space-y-2">
                {selectedEntities.map((entity, idx) => (
                  <div key={idx} className="flex items-center gap-2">
                    <Badge>{entity.entity_type}</Badge>
                    <span>{entity.text}</span>
                  </div>
                ))}
              </div>
            </div>
            
            <div className="flex justify-between mt-6">
              <Button variant="outline" onClick={onComplete}>
                Back to Documents
              </Button>
              <Button onClick={handleDownload}>
                Download Anonymized Document
              </Button>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            <div>
              <h3 className="text-lg font-medium mb-2">Select PII Entities to Anonymize</h3>
              <p className="text-sm text-gray-500 mb-4">
                Choose which personally identifiable information should be anonymized in the document.
              </p>
              
              {Object.entries(piiGroups).length === 0 ? (
                <p className="text-gray-500">No PII entities detected in this document</p>
              ) : (
                <div className="space-y-6">
                  {Object.entries(piiGroups).map(([type, entities]) => (
                    <div key={type} className="space-y-2">
                      <div className="flex items-center gap-2">
                        <h4 className="font-medium">{type}</h4>
                      </div>
                      <div className="space-y-2 pl-2 border-l-2 border-gray-200">
                        {entities.map((entity: any, idx) => (
                          <div key={idx} className="flex items-center gap-2">
                            <Checkbox 
                              id={`entity-${type}-${idx}`}
                              checked={isSelected(entity)}
                              onCheckedChange={() => handleCheck(entity)}
                            />
                            <label 
                              htmlFor={`entity-${type}-${idx}`} 
                              className="text-sm cursor-pointer"
                            >
                              {entity.text}
                            </label>
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
            
            {error && (
              <div className="p-3 text-red-600 bg-red-50 border border-red-200 rounded-md">
                {error}
              </div>
            )}
            
            <div className="flex justify-between">
              <Button variant="outline" onClick={onComplete} disabled={isProcessing}>
                Cancel
              </Button>
              <Button 
                onClick={handleAnonymize} 
                disabled={isProcessing || selectedEntities.length === 0}
              >
                {isProcessing ? 'Processing...' : 'Anonymize Document'}
              </Button>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
