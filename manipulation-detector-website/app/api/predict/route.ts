const maxUploadSize = 25 * 1024 * 1024;

export async function GET() {
  return Response.json({ configured: Boolean(process.env.MODEL_API_URL) });
}

export async function POST(request: Request) {
  const modelUrl = process.env.MODEL_API_URL;
  if (!modelUrl) {
    return Response.json(
      { error: 'The model endpoint is not configured. Set MODEL_API_URL in the website environment.' },
      { status: 503 },
    );
  }

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

  const modelForm = new FormData();
  modelForm.append('file', file, file.name);

  try {
    const modelResponse = await fetch(modelUrl, {
      method: 'POST',
      body: modelForm,
      cache: 'no-store',
    });
    return new Response(modelResponse.body, {
      status: modelResponse.status,
      headers: {
        'Content-Type': modelResponse.headers.get('content-type') ?? 'application/json',
        'Cache-Control': 'no-store',
      },
    });
  } catch {
    return Response.json({ error: 'Could not reach the configured model endpoint.' }, { status: 502 });
  }
}