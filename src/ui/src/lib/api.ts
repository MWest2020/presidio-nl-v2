// Get API base URL from environment or default to localhost for development
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const api = {
  // Upload a document with optional tags
  async uploadDocument(file: File, tags?: string[]) {
    const formData = new FormData();
    formData.append('file', file);
    if (tags && tags.length > 0) {
      formData.append('tags', JSON.stringify(tags));
    }
    
    const response = await fetch(`${API_BASE_URL}/documents/upload`, {
      method: 'POST',
      body: formData,
    });
    
    if (!response.ok) {
      throw new Error('Failed to upload document');
    }
    
    return response.json();
  },

  // Get document metadata and PII entities
  async getDocumentMetadata(fileId: string, includeDetails?: boolean) {
    const url = includeDetails 
      ? `${API_BASE_URL}/documents/${fileId}/metadata?details=true`
      : `${API_BASE_URL}/documents/${fileId}/metadata`;
    
    const response = await fetch(url);
    
    if (!response.ok) {
      throw new Error('Failed to get document metadata');
    }
    
    return response.json();
  },

  // Anonymize a document
  async anonymizeDocument(fileId: string, selectedEntities: string[]) {
    const response = await fetch(`${API_BASE_URL}/documents/${fileId}/anonymize`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ selected_entities: selectedEntities }),
    });
    
    if (!response.ok) {
      throw new Error('Failed to anonymize document');
    }
    
    return response.json();
  },

  // Download an anonymized document
  async downloadDocument(fileId: string): Promise<Blob> {
    const response = await fetch(`${API_BASE_URL}/documents/${fileId}/download`);
    
    if (!response.ok) {
      throw new Error('Failed to download document');
    }
    
    return response.blob();
  },

  // Get download URL for a document (used by anonymization form)
  getDocumentDownloadUrl(fileId: string): string {
    return `${API_BASE_URL}/documents/${fileId}/download`;
  },

  // Deanonymize a document (no key parameter needed based on usage)
  async deanonymizeDocument(file: File) {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await fetch(`${API_BASE_URL}/documents/deanonymize`, {
      method: 'POST',
      body: formData,
    });
    
    if (!response.ok) {
      throw new Error('Failed to deanonymize document');
    }
    
    return response.blob();
  },
}; 