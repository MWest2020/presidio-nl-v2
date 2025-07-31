import type { PiiEntityDto } from '../../types';

export function formatDate(date: string | Date): string {
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  return dateObj.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
}

export function groupPiiEntitiesByType(entities: PiiEntityDto[]) {
  return entities.reduce((groups, entity) => {
    const type = entity.entity_type;
    if (!groups[type]) {
      groups[type] = [];
    }
    groups[type].push(entity);
    return groups;
  }, {} as Record<string, PiiEntityDto[]>);
} 