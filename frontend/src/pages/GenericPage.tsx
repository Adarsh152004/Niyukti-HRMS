import * as React from 'react';
import { PageHeader, Card } from '@/components/ui/card';

interface GenericPageProps {
  title: string;
  description?: string;
}

export function GenericPage({ title, description }: GenericPageProps) {
  return (
    <div className="space-y-4">
      <PageHeader title={title} description={description} />
      <Card>
        <div className="py-8 text-center text-text-muted text-sm">
          <p className="font-medium text-text-secondary">{title}</p>
          <p className="mt-1 text-xs">This view connects to the backend API. Content loads when the server is running.</p>
        </div>
      </Card>
    </div>
  );
}
