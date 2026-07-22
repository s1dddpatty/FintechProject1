import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';

interface SummaryProps {
  totalPortfolio: number;
  averageLoan: number;
  averageIncome: number;
  averageInterest: number;
  isLoading?: boolean;
}

const formatCurrency = (val: number) =>
  new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(val);

const formatPercent = (val: number) =>
  new Intl.NumberFormat('en-US', { style: 'percent', maximumFractionDigits: 2 }).format(val / 100);

export default function PortfolioSummary({
  totalPortfolio,
  averageLoan,
  averageIncome,
  averageInterest,
  isLoading,
}: SummaryProps) {
  if (isLoading) {
    return (
      <Card className="rounded-xl shadow-sm border border-border bg-card">
        <CardHeader className="pb-2">
          <Skeleton className="h-5 w-1/3" />
        </CardHeader>
        <CardContent className="space-y-4 pt-4">
          {[1, 2, 3, 4, 5].map((i) => (
            <div key={i} className="flex justify-between items-center">
              <Skeleton className="h-4 w-1/4" />
              <Skeleton className="h-4 w-1/4" />
            </div>
          ))}
        </CardContent>
      </Card>
    );
  }

  const items = [
    { label: 'Total Portfolio', value: formatCurrency(totalPortfolio) },
    { label: 'Average Loan', value: formatCurrency(averageLoan) },
    { label: 'Average Income', value: formatCurrency(averageIncome) },
    { label: 'Average Interest', value: formatPercent(averageInterest) },
  ];

  return (
    <Card className="rounded-xl shadow-sm border border-border bg-card">
      <CardHeader className="pb-2 border-b border-border/50">
        <CardTitle className="text-sm font-medium">Portfolio Summary</CardTitle>
      </CardHeader>
      <CardContent className="pt-4">
        <div className="space-y-4">
          {items.map((item, idx) => (
            <div key={idx} className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">{item.label}</span>
              <span className="text-sm font-medium">{item.value}</span>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
