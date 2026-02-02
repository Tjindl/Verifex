"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Skeleton } from "@/components/ui/skeleton";
import { Separator } from "@/components/ui/separator";
import { AlertCircle, CheckCircle2, Code2, Play, Cpu, ShieldCheck, Activity, BrainCircuit } from "lucide-react";

export default function Home() {
  const [code, setCode] = useState("def factorial(n):\n    if n <= 1:\n        return 1\n    return n * factorial(n - 1)");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const analyzeCode = async () => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const res = await fetch("http://localhost:8000/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ code }),
      });

      if (!res.ok) {
        throw new Error(`Execution failed: ${res.statusText}`);
      }

      const data = await res.json();
      setResult(data);
    } catch (err: any) {
      setError(err.message || "An unexpected error occurred");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-50 p-6 md:p-12 font-sans selection:bg-blue-500/20">

      {/* Background Gradients */}
      <div className="fixed inset-0 z-0 pointer-events-none">
        <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] rounded-full bg-blue-500/10 blur-[120px]" />
        <div className="absolute bottom-[-20%] right-[-10%] w-[50%] h-[50%] rounded-full bg-purple-500/10 blur-[120px]" />
      </div>

      <div className="relative z-10 max-w-7xl mx-auto space-y-8">

        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="space-y-1">
            <h1 className="text-4xl font-extrabold tracking-tight flex items-center gap-3">
              <AppLogo />
              <span className="bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-purple-600 dark:from-blue-400 dark:to-purple-400">
                Verifex
              </span>
            </h1>
            <p className="text-lg text-slate-500 dark:text-slate-400 max-w-md">
              Neuro-symbolic verification for Python.
              <span className="block text-sm opacity-70">Powered by Gemini 2.0 Flash & Tree-sitter.</span>
            </p>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" size="sm" className="hidden md:flex">Documentation</Button>
            <Button variant="ghost" size="sm" className="hidden md:flex">GitHub</Button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 h-full">

          {/* Left Column: Input */}
          <div className="flex flex-col gap-4 h-full">
            <Card className="h-full border-slate-200 dark:border-slate-800 shadow-xl bg-white/50 dark:bg-slate-900/50 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Code2 className="w-5 h-5 text-blue-500" /> Source Code
                </CardTitle>
                <CardDescription>Paste the python function you want to verify.</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4 flex-1 flex flex-col">
                <div className="relative flex-1 group">
                  <div className="absolute inset-0 bg-gradient-to-b from-blue-500/5 to-purple-500/5 rounded-md pointer-events-none" />
                  <Textarea
                    placeholder="def foo(n): ..."
                    className="font-mono text-sm h-[500px] resize-none bg-slate-50/50 dark:bg-slate-950/50 border-slate-200 dark:border-slate-800 focus-visible:ring-blue-500/50"
                    value={code}
                    onChange={(e) => setCode(e.target.value)}
                    spellCheck={false}
                  />
                </div>
                <Button
                  size="lg"
                  className="w-full font-bold shadow-lg shadow-blue-500/20 transition-all hover:scale-[1.02] active:scale-[0.98] bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white"
                  onClick={analyzeCode}
                  disabled={loading || !code.trim()}
                >
                  {loading ? (
                    <>
                      <Cpu className="mr-2 h-4 w-4 animate-spin" /> Verifying Logic...
                    </>
                  ) : (
                    <>
                      <Play className="mr-2 h-4 w-4 fill-white" /> Analyze Correctness
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>
          </div>

          {/* Right Column: Output */}
          <div className="space-y-6">

            {error && (
              <Alert variant="destructive" className="animate-in fade-in slide-in-from-top-2">
                <AlertCircle className="h-4 w-4" />
                <AlertTitle>Analysis Failed</AlertTitle>
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            {!result && !loading && !error && (
              <div className="h-full flex flex-col items-center justify-center text-slate-400 p-12 border-2 border-dashed border-slate-200 dark:border-slate-800 rounded-xl bg-slate-50/50 dark:bg-slate-900/50">
                <Activity className="w-12 h-12 mb-4 opacity-20" />
                <p className="text-lg font-medium opacity-50">Ready to verify</p>
                <p className="text-sm opacity-40">Click analyze to begin formal verification</p>
              </div>
            )}

            {loading && (
              <div className="space-y-6 p-6 border border-slate-200 dark:border-slate-800 rounded-xl bg-white/50 dark:bg-slate-900/50">
                <div className="flex items-center gap-4">
                  <Skeleton className="h-10 w-10 rounded-full" />
                  <div className="space-y-2">
                    <Skeleton className="h-4 w-[200px]" />
                    <Skeleton className="h-4 w-[150px]" />
                  </div>
                </div>
                <Skeleton className="h-32 w-full rounded-lg" />
                <div className="grid grid-cols-2 gap-4">
                  <Skeleton className="h-24 w-full rounded-lg" />
                  <Skeleton className="h-24 w-full rounded-lg" />
                </div>
              </div>
            )}

            {result && (
              <div className="space-y-6 animate-in fade-in slide-in-from-bottom-8 duration-700">

                {/* Result Header */}
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-4 rounded-xl bg-slate-900 dark:bg-slate-900/50 text-white dark:text-white border border-transparent dark:border-slate-800 shadow-xl">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-green-500/20 rounded-lg">
                      <CheckCircle2 className="w-6 h-6 text-green-400 dark:text-green-500" />
                    </div>
                    <div>
                      <h3 className="font-bold text-lg">Verification Complete</h3>
                      <p className="text-sm opacity-80 font-mono text-green-300 dark:text-green-500">
                        {result.metadata.function_name}()
                      </p>
                    </div>
                  </div>
                  <Badge variant="outline" className="w-fit border-green-500/50 text-green-400 dark:text-green-500 dark:border-green-800 bg-green-500/10 px-4 py-1 text-sm font-mono">
                    SAFE
                  </Badge>
                </div>

                {/* Correctness & Complexity */}
                <div className="grid grid-cols-1 gap-6">
                  <Card className="bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 dark:from-slate-950 dark:via-slate-900 dark:to-slate-950 text-white dark:text-slate-200 border-0 shadow-2xl overflow-hidden relative">
                    <div className="absolute top-0 right-0 w-32 h-32 bg-blue-500/10 rounded-full blur-3xl" />
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2 text-white dark:text-white">
                        <BrainCircuit className="w-5 h-5 text-yellow-400 dark:text-blue-500" /> Correctness Argument
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="leading-relaxed text-slate-300 dark:text-slate-600 text-lg">
                        {result.explanation.correctness_argument}
                      </p>
                    </CardContent>
                  </Card>

                  <div className="grid grid-cols-2 gap-4">
                    <Card className="bg-white/50 dark:bg-slate-900/50 backdrop-blur-md border-orange-200 dark:border-orange-900/50">
                      <CardHeader className="p-4 pb-2">
                        <CardTitle className="text-sm font-medium text-slate-500 uppercase tracking-wider">Time Complexity</CardTitle>
                      </CardHeader>
                      <CardContent className="p-4 pt-0">
                        <div className="text-3xl font-black text-transparent bg-clip-text bg-gradient-to-r from-orange-500 to-red-500">
                          {result.explanation.complexity.time}
                        </div>
                      </CardContent>
                    </Card>
                    <Card className="bg-white/50 dark:bg-slate-900/50 backdrop-blur-md border-cyan-200 dark:border-cyan-900/50">
                      <CardHeader className="p-4 pb-2">
                        <CardTitle className="text-sm font-medium text-slate-500 uppercase tracking-wider">Space Complexity</CardTitle>
                      </CardHeader>
                      <CardContent className="p-4 pt-0">
                        <div className="text-3xl font-black text-transparent bg-clip-text bg-gradient-to-r from-cyan-500 to-blue-500">
                          {result.explanation.complexity.space}
                        </div>
                      </CardContent>
                    </Card>
                  </div>
                </div>

                {/* Invariants */}
                <Card className="bg-white/50 dark:bg-slate-900/50 backdrop-blur-md border-slate-200 dark:border-slate-800">
                  <CardHeader className="pb-2">
                    <CardTitle className="text-lg flex items-center gap-2">
                      <ShieldCheck className="w-5 h-5 text-purple-500" /> Invariants & Assumptions
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-6 pt-4">
                    <div className="space-y-3">
                      <div className="flex items-center gap-2 text-xs font-semibold uppercase text-slate-400 tracking-wider">
                        <div className="w-1.5 h-1.5 rounded-full bg-purple-500" />
                        Loop Invariants
                      </div>
                      <ul className="space-y-2">
                        {result.explanation.invariants?.map((inv: string, i: number) => (
                          <li key={i} className="flex gap-3 text-sm text-slate-700 dark:text-slate-300 bg-slate-100 dark:bg-slate-800/50 p-3 rounded-md border border-slate-200 dark:border-slate-800/50">
                            <span className="font-mono text-purple-500 shrink-0">Inv_{i}</span>
                            {inv}
                          </li>
                        ))}
                        {(!result.explanation.invariants || result.explanation.invariants.length === 0) && (
                          <li className="text-sm text-slate-400 italic">No formal invariants detected.</li>
                        )}
                      </ul>
                    </div>

                    <div className="space-y-3">
                      <div className="flex items-center gap-2 text-xs font-semibold uppercase text-slate-400 tracking-wider">
                        <div className="w-1.5 h-1.5 rounded-full bg-blue-500" />
                        Assumptions
                      </div>
                      <div className="flex flex-wrap gap-2">
                        {result.explanation.assumptions?.map((asm: string, i: number) => (
                          <Badge key={i} variant="secondary" className="font-normal bg-blue-50 text-blue-700 dark:bg-blue-900/20 dark:text-blue-300 hover:bg-blue-100 dark:hover:bg-blue-900/30 transition-colors py-1 px-3">
                            {asm}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  </CardContent>
                </Card>

              </div>
            )}

          </div>
        </div>
      </div>
    </div>
  );
}

function AppLogo() {
  return (
    <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-xl flex items-center justify-center text-white font-bold text-2xl shadow-lg shadow-blue-500/30 ring-1 ring-white/20">
      V
    </div>
  )
}
