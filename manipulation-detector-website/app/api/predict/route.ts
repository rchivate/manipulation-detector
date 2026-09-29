import { spawn } from 'node:child_process';
import path from 'node:path';

const maxUploadSize = 25 * 1024 * 1024;
const modelDirectory = path.resolve(process.cwd(), '../model/manipulation_detector');
const python = process.env.MODEL_PYTHON || process.env.PYTHON || 'python';

async function runModel(csv: string, health = false) {
  const output = await new Promise<string>((resolve, reject) => {
    const child = spawn(/*turbopackIgnore: true*/ python, ['-m', 'src.web_predict', ...(health ? ['--health'] : [])], {
      cwd: modelDirectory,
      windowsHide: true,
    });
    let stdout = '';
    let stderr = '';
    let settled = false;
    const timeout = setTimeout(() => child.kill(), 120_000);

    child.stdout.setEncoding('utf8');
    child.stderr.setEncoding('utf8');
    child.stdout.on('data', (chunk: string) => {
      stdout += chunk;
      if (stdout.length > 10 * 1024 * 1024) child.kill();
    });
    child.stderr.on('data', (chunk: string) => { stderr += chunk; });
    child.on('error', (error) => {
      if (!settled) {
        settled = true;
        clearTimeout(timeout);
        reject(error);
      }
    });
    child.on('close', (code) => {
      clearTimeout(timeout);
      if (settled) return;
      settled = true;
      if (code === 0) resolve(stdout);
      else reject(new Error(stderr.trim() || 'The local model process failed.'));
    });
    child.stdin.end(csv);
  });

  return JSON.parse(output) as Record<string, unknown>;
}

export async function GET() {
  try {
    const health = await runModel('', true);
    return Response.json({ configured: true, ...health });
  } catch (error) {
    const detail = error instanceof Error ? error.message : 'Unable to start the local model.';
    return Response.json({ configured: false, error: detail }, { status: 503 });
  }
}

export async function POST(request: Request) {
  const formData = await request.formData();
  const file = formData.get('file');
  if (!(file instanceof File)) {
    return Response.json({ error: 'Attach a CSV file under the "file" field.' }, { status: 400 });
  }
  if (!file.name.toLowerCase().endsWith('.csv')) {
    return Response.json({ error: 'Only CSV files are supported.' }, { status: 400 });
  }
  if (file.size > maxUploadSize) {
    return Response.json({ error: 'The file exceeds the 25 MB upload limit.' }, { status: 413 });
  }

  try {
    const prediction = await runModel(await file.text());
    return Response.json(prediction, { headers: { 'Cache-Control': 'no-store' } });
  } catch (error) {
    const detail = error instanceof Error ? error.message : 'The local model could not analyze this CSV.';
    const isCsvError = detail.includes('CSV') || detail.includes('text column') || detail.includes('500 rows');
    return Response.json({ error: detail }, { status: isCsvError ? 400 : 503 });
  }
}