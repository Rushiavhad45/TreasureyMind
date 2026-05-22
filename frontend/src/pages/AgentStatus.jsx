import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { agentAPI } from "../services/api";
import {
  Play,
  Bot,
  CheckCircle,
  XCircle,
  Clock,
  AlertCircle,
  ChevronDown,
  ChevronUp,
  Zap,
  Activity,
  BarChart2,
  Shield,
  ClipboardCheck,
  DollarSign,
} from "lucide-react";
import { format } from "date-fns";

const AGENT_META = {
  CashFlowAgent: {
    icon: Activity,
    color: "#22d3ee",
    description: "Analyzes transactions, calculates inflow/outflow, generates cash flow summary",
  },
  ForecastAgent: {
    icon: BarChart2,
    color: "#a78bfa",
    description: "Predicts future cash flow, identifies trends, forecasts liquidity",
  },
  AllocationAgent: {
    icon: DollarSign,
    color: "#34d399",
    description: "Analyzes surplus funds, suggests optimal allocation, prioritizes liabilities",
  },
  RiskAlertAgent: {
    icon: Shield,
    color: "#f97316",
    description: "Detects risks, monitors thresholds, generates alerts using Gemini",
  },
  ApprovalAgent: {
    icon: ClipboardCheck,
    color: "#f59e0b",
    description: "Reviews AI suggestions, creates approval records, maintains audit logs",
  },
};

const StatusBadge = ({ status }) => {
  const config = {
    completed: { icon: CheckCircle, label: "Completed", cls: "badge-success" },
    failed: { icon: XCircle, label: "Failed", cls: "badge-danger" },
    running: { icon: Clock, label: "Running", cls: "badge-info" },
    pending: { icon: AlertCircle, label: "Pending", cls: "badge-warning" },
  };
  const c = config[status] || config.pending;
  const Icon = c.icon;
  return (
    <span className={`tm-badge ${c.cls}`} style={{ display: "inline-flex", alignItems: "center", gap: 4 }}>
      <Icon size={12} />
      {c.label}
    </span>
  );
};

const AgentCard = ({ log }) => {
  const [expanded, setExpanded] = useState(false);
  const meta = AGENT_META[log.agent_name] || { icon: Bot, color: "#94a3b8", description: "" };
  const Icon = meta.icon;

  return (
    <div className="tm-card" style={{ marginBottom: 12, border: `1px solid ${meta.color}22` }}>
      <div
        style={{ display: "flex", alignItems: "center", gap: 16, cursor: "pointer" }}
        onClick={() => setExpanded(!expanded)}
      >
        <div
          style={{
            width: 44,
            height: 44,
            borderRadius: 10,
            background: `${meta.color}18`,
            border: `1px solid ${meta.color}44`,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            flexShrink: 0,
          }}
        >
          <Icon size={20} style={{ color: meta.color }} />
        </div>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap" }}>
            <span style={{ fontWeight: 600, color: "var(--text-primary)" }}>{log.agent_name}</span>
            <StatusBadge status={log.status} />
            {log.duration_seconds && (
              <span style={{ fontSize: 11, color: "var(--text-muted)" }}>
                {log.duration_seconds ? `${log.duration_seconds.toFixed(2)}s` : ""}
              </span>
            )}
          </div>
          <div style={{ fontSize: 12, color: "var(--text-secondary)", marginTop: 2 }}>
            {meta.description}
          </div>
          {log.started_at && (
            <div style={{ fontSize: 11, color: "var(--text-muted)", marginTop: 2 }}>
              {format(new Date(log.started_at), "MMM d, yyyy HH:mm:ss")}
            </div>
          )}
        </div>
        <div style={{ color: "var(--text-muted)", flexShrink: 0 }}>
          {expanded ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
        </div>
      </div>

      {expanded && (
        <div style={{ marginTop: 16, borderTop: "1px solid var(--border)", paddingTop: 16 }}>
          {log.input_data && (
            <div style={{ marginBottom: 12 }}>
              <div style={{ fontSize: 11, fontWeight: 600, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: 1, marginBottom: 6 }}>
                Input Data
              </div>
              <pre style={{
                background: "var(--bg-secondary)",
                padding: 12,
                borderRadius: 8,
                fontSize: 12,
                color: "var(--accent-cyan)",
                overflowX: "auto",
                margin: 0,
                fontFamily: "'JetBrains Mono', monospace",
              }}>
                {JSON.stringify(log.input_data, null, 2)}
              </pre>
            </div>
          )}
          {log.output_data && (
            <div style={{ marginBottom: 12 }}>
              <div style={{ fontSize: 11, fontWeight: 600, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: 1, marginBottom: 6 }}>
                Output Data
              </div>
              <pre style={{
                background: "var(--bg-secondary)",
                padding: 12,
                borderRadius: 8,
                fontSize: 12,
                color: "#34d399",
                overflowX: "auto",
                margin: 0,
                fontFamily: "'JetBrains Mono', monospace",
              }}>
                {JSON.stringify(log.output_data, null, 2)}
              </pre>
            </div>
          )}
          {log.reasoning && (
            <div>
              <div style={{ fontSize: 11, fontWeight: 600, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: 1, marginBottom: 6 }}>
                AI Reasoning (Gemini)
              </div>
              <div style={{
                background: "rgba(167,139,250,0.08)",
                border: "1px solid rgba(167,139,250,0.2)",
                padding: 12,
                borderRadius: 8,
                fontSize: 13,
                color: "var(--text-secondary)",
                lineHeight: 1.6,
              }}>
                {log.reasoning}
              </div>
            </div>
          )}
          {log.error_message && (
            <div>
              <div style={{ fontSize: 11, fontWeight: 600, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: 1, marginBottom: 6 }}>
                Error
              </div>
              <div style={{
                background: "rgba(239,68,68,0.08)",
                border: "1px solid rgba(239,68,68,0.2)",
                padding: 12,
                borderRadius: 8,
                fontSize: 13,
                color: "#f87171",
              }}>
                {log.error_message}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default function AgentStatus() {
  const queryClient = useQueryClient();
  const [selectedRun, setSelectedRun] = useState(null);

  const { data: statusData, isLoading } = useQuery({
    queryKey: ["agent-status"],
    queryFn: () => agentAPI.status().then((r) => r.data),
    refetchInterval: 10000,
  });

  const { data: logsData } = useQuery({
    queryKey: ["agent-logs", selectedRun],
    queryFn: () => agentAPI.logs({ pipeline_run_id: selectedRun, page_size: 50 }).then((r) => r.data),
    refetchInterval: 5000,
  });

  const triggerMutation = useMutation({
    mutationFn: () => agentAPI.trigger(),
    onSuccess: (data) => {
      setSelectedRun(data.data.pipeline_run_id);
      queryClient.invalidateQueries(["agent-status"]);
      queryClient.invalidateQueries(["agent-logs"]);
    },
  });

  const agentOrder = ["CashFlowAgent", "ForecastAgent", "AllocationAgent", "RiskAlertAgent", "ApprovalAgent"];

  // Group logs by pipeline_run_id for run selector
  const runs = logsData?.pipeline_runs || [];
  const logs = logsData?.results || [];

  // Latest run summary from status endpoint
  const latestRun = statusData?.latest_run;
  const agentStats = statusData?.agent_stats || {};

  return (
    <div>
      {/* Header */}
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 24, flexWrap: "wrap", gap: 12 }}>
        <div>
          <h1 style={{ fontSize: 24, fontWeight: 700, color: "var(--text-primary)", margin: 0 }}>
            Agent Status
          </h1>
          <p style={{ color: "var(--text-secondary)", margin: "4px 0 0", fontSize: 14 }}>
            Multi-agent pipeline orchestration & real-time monitoring
          </p>
        </div>
        <button
          className="tm-btn"
          onClick={() => triggerMutation.mutate()}
          disabled={triggerMutation.isPending}
          style={{ display: "flex", alignItems: "center", gap: 8 }}
        >
          {triggerMutation.isPending ? (
            <>
              <Clock size={16} className="spin" /> Running Pipeline...
            </>
          ) : (
            <>
              <Play size={16} /> Trigger Pipeline
            </>
          )}
        </button>
      </div>

      {triggerMutation.isSuccess && (
        <div style={{
          background: "rgba(52,211,153,0.1)",
          border: "1px solid rgba(52,211,153,0.3)",
          borderRadius: 10,
          padding: "12px 16px",
          marginBottom: 20,
          color: "#34d399",
          fontSize: 14,
        }}>
          ✓ Pipeline triggered successfully. Run ID: <strong>{triggerMutation.data?.data?.pipeline_run_id}</strong>
        </div>
      )}

      {/* Pipeline flow diagram */}
      <div className="tm-card" style={{ marginBottom: 24 }}>
        <div style={{ fontSize: 13, fontWeight: 600, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: 1, marginBottom: 16 }}>
          Pipeline Architecture
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 0, overflowX: "auto", paddingBottom: 8 }}>
          {agentOrder.map((name, i) => {
            const meta = AGENT_META[name];
            const Icon = meta.icon;
            const stat = agentStats[name] || {};
            return (
              <div key={name} style={{ display: "flex", alignItems: "center", flexShrink: 0 }}>
                <div style={{ textAlign: "center" }}>
                  <div style={{
                    width: 56,
                    height: 56,
                    borderRadius: 14,
                    background: `${meta.color}15`,
                    border: `2px solid ${meta.color}50`,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    margin: "0 auto 6px",
                  }}>
                    <Icon size={22} style={{ color: meta.color }} />
                  </div>
                  <div style={{ fontSize: 11, fontWeight: 600, color: "var(--text-secondary)", maxWidth: 70, lineHeight: 1.3 }}>
                    {name.replace("Agent", "")}
                  </div>
                  {stat.total_runs !== undefined && (
                    <div style={{ fontSize: 10, color: "var(--text-muted)", marginTop: 2 }}>
                      {stat.success_rate || 0}% success
                    </div>
                  )}
                </div>
                {i < agentOrder.length - 1 && (
                  <div style={{ display: "flex", alignItems: "center", margin: "0 6px", color: "var(--text-muted)" }}>
                    <div style={{ width: 20, height: 2, background: "var(--border)" }} />
                    <div style={{ width: 0, height: 0, borderTop: "5px solid transparent", borderBottom: "5px solid transparent", borderLeft: "7px solid var(--border)" }} />
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Stats row */}
      {statusData && (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: 16, marginBottom: 24 }}>
          {[
            { label: "Total Pipeline Runs", value: statusData.total_pipeline_runs || 0, color: "#22d3ee" },
            { label: "Agents Active", value: "5 / 5", color: "#34d399" },
            { label: "Last Run Status", value: latestRun?.status || "N/A", color: latestRun?.status === "completed" ? "#34d399" : "#f97316" },
            { label: "Avg Exec Time", value: statusData.avg_execution_time ? `${statusData.avg_execution_time}ms` : "—", color: "#a78bfa" },
          ].map((s) => (
            <div key={s.label} className="tm-card" style={{ textAlign: "center", padding: 16 }}>
              <div style={{ fontSize: 22, fontWeight: 700, color: s.color }}>{s.value}</div>
              <div style={{ fontSize: 11, color: "var(--text-muted)", marginTop: 4 }}>{s.label}</div>
            </div>
          ))}
        </div>
      )}

      {/* Agent Logs */}
      <div className="tm-card">
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 16, flexWrap: "wrap", gap: 8 }}>
          <div style={{ fontSize: 13, fontWeight: 600, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: 1 }}>
            Agent Execution Logs
          </div>
          <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
            <Zap size={14} style={{ color: "#f59e0b" }} />
            <span style={{ fontSize: 12, color: "var(--text-muted)" }}>
              Auto-refreshes every 5s
            </span>
          </div>
        </div>

        {isLoading ? (
          <div style={{ textAlign: "center", padding: 40, color: "var(--text-muted)" }}>
            Loading agent logs...
          </div>
        ) : logs.length === 0 ? (
          <div style={{ textAlign: "center", padding: 40 }}>
            <Bot size={40} style={{ color: "var(--text-muted)", marginBottom: 12 }} />
            <div style={{ color: "var(--text-muted)", marginBottom: 8 }}>No agent runs yet</div>
            <div style={{ fontSize: 13, color: "var(--text-muted)" }}>
              Click "Trigger Pipeline" to start the multi-agent workflow
            </div>
          </div>
        ) : (
          logs.map((log) => <AgentCard key={log.id} log={log} />)
        )}
      </div>

      <style>{`
        .spin { animation: spin 1s linear infinite; }
        @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
      `}</style>
    </div>
  );
}
