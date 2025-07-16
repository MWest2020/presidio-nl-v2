export interface DocumentDto {
  id: string;
  filename: string;
  content_type: string;
  uploaded_at: string;
  tags: DocumentTagDto[];
  pii_entities: PiiEntityDto[];
}

export interface DocumentTagDto {
  id: string;
  name: string;
}

export interface PiiEntityDto {
  entity_type: string;
  text: string;
  start: number;
  end: number;
  score?: number;
}


export interface DocumentAnonymizationResponse {
  id: string;
  filename: string;
  anonymized_at: string;
  time_taken: number;
  status: string;
  pii_entities: PiiEntityDto[];
}

export interface AddDocumentResponseSuccess {
  files: DocumentDto[];
}
