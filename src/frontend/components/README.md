# Valuation Dashboard Component

A React component for displaying business valuation data including valuation meters, driver scorecards, and timeline charts.

## Features

1. **Valuation Meter** - Shows estimated enterprise value range with low/high/average markers
2. **Driver Scorecards** - Six cards displaying each Matador driver score (0-100)
3. **Value Timeline** - Chart showing valuation trends over time

## Installation

This component uses:
- React (with TypeScript)
- Tailwind CSS (already configured in the project)

No additional dependencies required for basic functionality. For enhanced timeline charts, you can optionally add:
```bash
npm install recharts
```

## Usage

```tsx
import ValuationDashboard from './components/ValuationDashboard';

function App() {
  return (
    <ValuationDashboard 
      tenantId="your-tenant-uuid"
      apiBaseUrl="http://localhost:8000" // Optional, defaults to env var
    />
  );
}
```

## API Endpoints Required

The component expects these API endpoints:

- `GET /api/valuation/snapshot?tenant_id={tenantId}` - Latest valuation snapshot
- `GET /api/valuation/drivers?tenant_id={tenantId}` - Driver scores
- `GET /api/valuation/snapshots?tenant_id={tenantId}` - Historical snapshots (optional, for timeline)

## Component Props

```typescript
interface ValuationDashboardProps {
  tenantId: string;        // Required: Tenant UUID
  apiBaseUrl?: string;     // Optional: API base URL (defaults to REACT_APP_API_URL or localhost:8000)
}
```

## Styling

The component uses Tailwind CSS with the project's existing dark theme:
- Background: `slate-950`
- Cards: `slate-900` with `slate-800` borders
- Accent colors:
  - Emerald (above average, high scores)
  - Blue (average)
  - Amber (below average, medium scores)
  - Red (low scores)

## Data Structure

The component expects data matching the API response structure from `src/main.py`:

```typescript
interface ValuationSnapshot {
  id: string;
  tenant_id: string;
  as_of_date: string;
  ttm_revenue: number;
  ttm_sde: number;
  ttm_ebitda: number;
  tier: 'below_avg' | 'avg' | 'above_avg';
  multiple_low: number;
  multiple_high: number;
  ev_low: number;
  ev_high: number;
  confidence_score: number;
  drivers_json?: Record<string, number>;
}
```

## Integration with React App

If you're building a React app, add this to your component tree:

```tsx
// App.tsx or Dashboard.tsx
import ValuationDashboard from './components/ValuationDashboard';

function DashboardPage() {
  const tenantId = useTenantId(); // Get from auth context or props
  
  return (
    <div>
      <ValuationDashboard tenantId={tenantId} />
    </div>
  );
}
```

## Future Enhancements

- Add historical snapshots endpoint for timeline
- Integrate recharts for more sophisticated timeline visualization
- Add export functionality for valuation reports
- Add scenario simulation controls





