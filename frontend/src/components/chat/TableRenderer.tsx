import React from 'react';

export interface TableData {
  headers: string[];
  alignments: ('left' | 'center' | 'right')[];
  rows: string[][];
}

interface TableRendererProps {
  table: TableData;
  parseInline?: (text: string) => React.ReactNode;
}

export const TableRenderer: React.FC<TableRendererProps> = ({ table, parseInline = (t) => t }) => {
  if (!table || (table.headers.length === 0 && table.rows.length === 0)) {
    return null;
  }

  return (
    <div className="my-4 overflow-hidden rounded-xl border border-border bg-surface shadow-sm">
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs border-collapse">
          {table.headers.length > 0 && (
            <thead className="bg-surface-secondary border-b border-border text-text-primary font-semibold tracking-wide">
              <tr>
                {table.headers.map((th, i) => {
                  const align = table.alignments[i] || 'left';
                  const alignClass =
                    align === 'center' ? 'text-center' : align === 'right' ? 'text-right' : 'text-left';
                  return (
                    <th key={i} className={`py-3 px-4 text-[11px] font-semibold tracking-wider text-text-muted uppercase ${alignClass}`}>
                      {parseInline(th)}
                    </th>
                  );
                })}
              </tr>
            </thead>
          )}
          <tbody className="divide-y divide-border">
            {table.rows.map((row, rIdx) => (
              <tr
                key={rIdx}
                className={`transition-colors duration-150 ${
                  rIdx % 2 === 0 ? 'bg-transparent' : 'bg-surface-secondary/30'
                } hover:bg-surface-secondary/70`}
              >
                {row.map((cell, cIdx) => {
                  const align = table.alignments[cIdx] || 'left';
                  const alignClass =
                    align === 'center' ? 'text-center' : align === 'right' ? 'text-right' : 'text-left';
                  return (
                    <td key={cIdx} className={`py-2.5 px-4 text-text-secondary leading-relaxed ${alignClass}`}>
                      {parseInline(cell)}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default TableRenderer;
