import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { api } from '../lib/api';
import { downloadBlob } from '../lib/utils';

export function DeanonymizeForm() {
  const [file, setFile] = useState<File | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
      setError(null);
    }
  };
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!file) {
      setError('Please select a file');
      return;
    }
    
    setIsLoading(true);
    setError(null);
    
    try {
      const blob = await api.deanonymizeDocument(file);
      
      // Create a download link
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `deanonymized_${file.name}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      
      setSuccess(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Deanonymization failed');
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <Card className="mb-6">
      <CardHeader>
        <CardTitle>Deanonymize Document</CardTitle>
      </CardHeader>
      <CardContent>
        {success ? (
          <div className="p-4 border border-green-200 bg-green-50 rounded-md">
            <p className="text-green-700">Document successfully deanonymized and downloaded!</p>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <Input 
                type="file" 
                onChange={handleFileChange} 
                accept=".pdf"
                disabled={isLoading}
              />
              <p className="mt-1 text-xs text-gray-500">
                Upload a previously anonymized PDF document
              </p>
            </div>
            
            {error && <p className="text-red-500 text-sm">{error}</p>}
            
            <Button type="submit" disabled={isLoading || !file}>
              {isLoading ? 'Processing...' : 'Deanonymize Document'}
            </Button>
          </form>
        )}
      </CardContent>
    </Card>
  );
}
