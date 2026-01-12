import { FileText } from "lucide-react";
import { cn } from "@/lib/utils";

export function Brand({ compact = false, inverse = false, className }: { compact?: boolean; inverse?: boolean; className?: string }) {
  return (
    <div className={cn("flex items-center gap-2.5", className)}>
      <div className={cn("grid h-8 w-8 place-items-center rounded-lg shadow-sm", inverse ? "bg-white text-slate-950" : "bg-slate-950 text-white")}>
        <FileText className="h-4 w-4" strokeWidth={1.8} />
      </div>
      {!compact && (
        <div className="leading-none">
          <div className={cn("text-sm font-semibold tracking-[-0.02em]", inverse && "text-white")}>DocChat</div>
          <div className={cn("mt-1 text-[9px] font-medium uppercase tracking-[0.14em]", inverse ? "text-slate-400" : "text-muted-foreground")}>Local intelligence</div>
        </div>
      )}
    </div>
  );
}
