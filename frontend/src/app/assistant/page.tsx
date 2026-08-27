'use client';
import React, { useState } from 'react';
import { Bot, Send, BrainCircuit, CheckCircle2, Wrench, FileText, Sparkles } from 'lucide-react';
import { api } from '@/lib/api';
import { AgentRunResponse } from '@/lib/types';

export default function AssistantPage() {
  const [prompt, setPrompt] = useState('Design a thermally efficient shelter for Leh, Ladakh.');
  const [response, setResponse] = useState<AgentRunResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [report, setReport] = useState<string | null>(null);

  const handleRunAgent = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!prompt.trim()) return;

    setIsLoading(true);
    try {
      const res = await api.runAgent(prompt, "Leh, Ladakh", 34.1526, 77.5771);
      setResponse(res);
      const rpt = await api.generateReport("Leh, Ladakh", 34.1526, 77.5771);
      setReport(rpt.content_markdown);
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-6xl mx-auto font-sans">
      {/* HEADER */}
      <div className="bg-[#16171d] border border-[#2e303a] p-6 rounded-2xl flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <span className="text-[10px] font-mono text-blue-400 font-bold tracking-widest uppercase block mb-1">
            AGENTIC AI DECISION SUPPORT ASSISTANT
          </span>
          <h1 className="text-2xl font-bold text-white tracking-tight m-0 flex items-center gap-2">
            <Bot className="text-blue-400" size={24} />
            <span>AI Orchestrated Engineering Agent</span>
          </h1>
          <p className="text-sm text-gray-400 mt-1">
            Executes structured tools for climate data, ML surrogate predictions, optimization, and ANSYS validation.
          </p>
        </div>
      </div>

      {/* PROMPT INPUT FORM */}
      <div className="bg-[#16171d] border border-[#2e303a] p-4 rounded-2xl">
        <form onSubmit={handleRunAgent} className="flex gap-3">
          <input
            type="text"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Ask AI: e.g. Design a thermally efficient shelter for hot arid desert climate..."
            className="flex-1 bg-[#121319] border border-[#2e303a] rounded-xl px-4 py-3 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-blue-500 font-mono"
          />
          <button
            type="submit"
            disabled={isLoading}
            className="bg-blue-600 hover:bg-blue-500 text-white font-mono text-xs px-6 py-3 rounded-xl flex items-center gap-2 transition-all"
          >
            <Send size={15} />
            <span>{isLoading ? "Orchestrating Tools..." : "Run AI Agent"}</span>
          </button>
        </form>

        {/* PRESET PROMPTS */}
        <div className="flex flex-wrap gap-2 mt-3 text-[11px] font-mono">
          <span className="text-gray-500 flex items-center gap-1"><Sparkles size={12} /> Presets:</span>
          {[
            "Design a thermally efficient shelter for Leh, Ladakh.",
            "Optimize shelter for extreme desert heat in Cairo, Egypt.",
            "Evaluate timber vs stabilized earth block for cold climate."
          ].map((preset) => (
            <button
              key={preset}
              onClick={() => {
                setPrompt(preset);
              }}
              className="bg-[#121319] hover:bg-[#222530] text-gray-300 border border-[#2e303a] px-2.5 py-1 rounded-lg text-[10px]"
            >
              {preset}
            </button>
          ))}
        </div>
      </div>

      {/* AGENT RESPONSE & TOOL LOGS */}
      {response && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* TOOL EXECUTION LOG */}
          <div className="lg:col-span-5 bg-[#16171d] border border-[#2e303a] p-5 rounded-2xl space-y-4 font-mono">
            <div className="border-b border-[#2e303a] pb-3 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Wrench size={16} className="text-amber-400" />
                <h3 className="text-sm font-bold text-white uppercase m-0">Structured Tool Execution Log</h3>
              </div>
              <span className="text-[10px] text-emerald-400 bg-emerald-950 px-2 py-0.5 rounded border border-emerald-800">
                {response.tool_calls.length} TOOLS EXECUTED
              </span>
            </div>

            <div className="space-y-3 max-h-[500px] overflow-y-auto pr-1">
              {response.tool_calls.map((log, idx) => (
                <div key={idx} className="p-3 bg-[#121319] border border-[#2e303a] rounded-xl space-y-1 text-xs">
                  <div className="flex justify-between items-center text-[11px]">
                    <span className="font-bold text-blue-400">{log.tool_name}()</span>
                    <span className="text-[10px] text-gray-500">{log.timestamp}</span>
                  </div>
                  <pre className="text-[10px] text-gray-400 bg-[#0a0b0e] p-2 rounded border border-[#1e202a] overflow-x-auto">
                    {JSON.stringify(log.output, null, 2)}
                  </pre>
                </div>
              ))}
            </div>
          </div>

          {/* AGENT RECOMMENDATION & REPORT */}
          <div className="lg:col-span-7 bg-[#16171d] border border-[#2e303a] p-5 rounded-2xl space-y-5">
            <div className="border-b border-[#2e303a] pb-3 flex items-center gap-2">
              <BrainCircuit size={18} className="text-blue-400" />
              <h3 className="text-sm font-bold text-white font-mono uppercase m-0">AI Decision Support Explanation</h3>
            </div>

            <div className="bg-[#121319] border border-[#2e303a] p-5 rounded-xl text-xs text-gray-300 space-y-3 leading-relaxed">
              <div className="prose prose-invert max-w-none">
                <div dangerouslySetInnerHTML={{ __html: response.response.replace(/\n/g, '<br/>') }} />
              </div>
            </div>

            {report && (
              <div className="bg-[#121319] border border-[#2e303a] p-5 rounded-xl space-y-3 font-mono">
                <div className="flex items-center gap-2 text-white font-bold text-xs border-b border-[#2e303a] pb-2">
                  <FileText size={16} className="text-emerald-400" />
                  <span>Executive Engineering Report Preview</span>
                </div>
                <pre className="text-[10px] text-gray-300 overflow-x-auto max-h-60 leading-relaxed font-mono">
                  {report}
                </pre>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
