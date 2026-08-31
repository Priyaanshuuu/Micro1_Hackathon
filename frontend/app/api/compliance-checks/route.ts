import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

export async function GET() {
  try {
    const filePath = path.join(process.cwd(), '..', 'rfp-auto-responder', 'output', 'compliance_checks.json');

    // If file doesn't exist, return empty array (no checks yet)
    if (!fs.existsSync(filePath)) {
      return NextResponse.json({
        recent_checks: [],
        message: 'No compliance checks recorded yet. Run evaluation to populate.'
      });
    }

    const data = JSON.parse(fs.readFileSync(filePath, 'utf-8'));

    // Return last 20 checks
    const recentChecks = (data.checks || []).slice(-20);

    return NextResponse.json({ recent_checks: recentChecks });
  } catch (error) {
    console.error('Error reading compliance checks:', error);
    return NextResponse.json({ recent_checks: [] }, { status: 200 });
  }
}
