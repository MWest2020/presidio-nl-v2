import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import type { DocumentDto } from "../types";
import { api } from "../lib/api";

interface DocumentUploadProps {
  onUploadSuccess: (documents: DocumentDto[]) => void;
}

export function DocumentUpload({ onUploadSuccess }: DocumentUploadProps) {
  const [file, setFile] = useState<File | null>(null);
  const [tags, setTags] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

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
      // Add tags if provided
      const tagList = tags.split(',').map(tag => tag.trim()).filter(Boolean);
      
      // Use the api.uploadDocument function
      const documents = await api.uploadDocument(file, tagList);
      onUploadSuccess(documents);
      
      // Reset form
      setFile(null);
      setTags('');
      
      // Reset file input
      const fileInput = document.querySelector('input[type=file]') as HTMLInputElement;
      if (fileInput) fileInput.value = '';
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card className="mb-6">
      <CardHeader>
        <CardTitle>Upload Document</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <Input 
              type="file" 
              onChange={handleFileChange} 
              accept=".pdf"
              disabled={isLoading}
            />
            <p className="mt-1 text-xs text-gray-500">Only PDF files are supported</p>
          </div>
          
          <div>
            <label htmlFor="tags" className="block text-sm font-medium mb-1">
              Tags (comma separated)
            </label>
            <Input
              id="tags"
              value={tags}
              onChange={(e) => setTags(e.target.value)}
              placeholder="personal, financial, medical"
              disabled={isLoading}
            />
          </div>
          
          {error && <p className="text-red-500 text-sm">{error}</p>}
          
          <Button type="submit" disabled={isLoading}>
            {isLoading ? 'Uploading...' : 'Upload Document'}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
