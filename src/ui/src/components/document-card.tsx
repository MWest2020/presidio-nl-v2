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
    <Card className="h-full flex flex-col">
      <CardHeader className="flex-none">
        <CardTitle className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2 text-base sm:text-lg">
          <span className="truncate max-w-full">{document.filename}</span>
          <Badge className="whitespace-nowrap">{document.content_type}</Badge>
        </CardTitle>
        <p className="text-xs sm:text-sm text-gray-500">Uploaded: {formatDate(document.uploaded_at)}</p>
      </CardHeader>
      <CardContent className="flex-grow">
        {document.tags.length > 0 && (
          <div className="flex flex-wrap gap-1 mb-3">
            {document.tags.map(tag => (
              <Badge key={tag.id} variant="secondary" className="text-xs">{tag.name}</Badge>
            ))}
          </div>
        )}
      </CardContent>
      <CardFooter className="flex flex-col sm:flex-row sm:justify-end gap-2 mt-auto">
        <Button variant="outline" onClick={() => onViewClick(document.id)} className="w-full sm:w-auto">
          View Details
        </Button>
        <Button onClick={() => onAnonymizeClick(document.id)} className="w-full sm:w-auto">
          Anonymize
        </Button>
      </CardFooter>
    </Card>
  );
}
