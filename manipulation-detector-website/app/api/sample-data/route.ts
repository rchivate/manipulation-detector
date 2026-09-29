import { readFile } from 'node:fs/promises';
import path from 'node:path';

export async function GET() {
  const samplePath = path.resolve(process.cwd(), '../model/manipulation_detector/data/sample.csv');
  const sample = await readFile(samplePath, 'utf8');
  return new Response(sample, {
    headers: {
      'Content-Type': 'text/csv; charset=utf-8',
      'Content-Disposition': 'attachment; filename="manipulation-sample.csv"',
      'Cache-Control': 'no-store',
    },
  });
}