import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import { formatDate } from "../lib/utils";
import type { DocumentDto } from "../types";

interface DocumentCardProps {
  document: DocumentDto;
  onViewClick: (id: string) => void;
  onAnonymizeClick: (id: string) => void;
}

export function DocumentCard({ document, onViewClick, onAnonymizeClick }: DocumentCardProps) {
  return (
    <Card className="mb-4">
      <CardHeader>
        <CardTitle className="flex justify-between items-center">
          <span>{document.filename}</span>
          <Badge>{document.content_type}</Badge>
        </CardTitle>
        <p className="text-sm text-gray-500">Uploaded: {formatDate(document.uploaded_at)}</p>
      </CardHeader>
      <CardContent>
        {document.tags.length > 0 && (
          <div className="flex flex-wrap gap-1 mb-3">
            {document.tags.map(tag => (
              <Badge key={tag.id} variant="secondary">{tag.name}</Badge>
            ))}
          </div>
        )}
      </CardContent>
      <CardFooter className="flex justify-end gap-2">
        <Button variant="outline" onClick={() => onViewClick(document.id)}>
          View Details
        </Button>
        <Button onClick={() => onAnonymizeClick(document.id)}>
          Anonymize
        </Button>
      </CardFooter>
    </Card>
  );
}
