"use client";

import { createContext, useContext, useEffect, useReducer, useState } from "react";
import { DemoState, initialState } from "@/data/demo-data";
import { clearStored, loadStored, saveStored } from "@/lib/storage";

type Action =
  | { type: "hydrate"; state: DemoState }
  | { type: "patch"; value: Partial<DemoState> }
  | { type: "candidate"; value: Partial<DemoState["candidate"]> }
  | { type: "toggleJob"; id: string }
  | { type: "toggleLearning"; id: string }
  | { type: "suggestion"; id: string; decision: "accepted" | "rejected" }
  | { type: "reset" };

function reducer(state: DemoState, action: Action): DemoState {
  if (action.type === "hydrate") return action.state;
  if (action.type === "patch") return { ...state, ...action.value };
  if (action.type === "candidate") return { ...state, candidate: { ...state.candidate, ...action.value } };
  if (action.type === "toggleJob") return { ...state, savedJobs: state.savedJobs.includes(action.id) ? state.savedJobs.filter((id) => id !== action.id) : [...state.savedJobs, action.id] };
  if (action.type === "toggleLearning") return { ...state, completedLearning: state.completedLearning.includes(action.id) ? state.completedLearning.filter((id) => id !== action.id) : [...state.completedLearning, action.id] };
  if (action.type === "suggestion") return { ...state, suggestionDecisions: { ...state.suggestionDecisions, [action.id]: action.decision } };
  return initialState;
}

const DemoContext = createContext<{ state: DemoState; dispatch: React.Dispatch<Action>; ready: boolean } | null>(null);

export function DemoProvider({ children }: { children: React.ReactNode }) {
  const [state, dispatch] = useReducer(reducer, initialState);
  const [ready, setReady] = useState(false);
  useEffect(() => { const timer = window.setTimeout(() => { dispatch({ type: "hydrate", state: loadStored(initialState) }); setReady(true); }, 0); return () => window.clearTimeout(timer); }, []);
  useEffect(() => { if (ready) saveStored(state); }, [state, ready]);
  return <DemoContext.Provider value={{ state, dispatch, ready }}><div data-demo-ready={ready} aria-busy={!ready}>{children}</div></DemoContext.Provider>;
}

export function useDemo() {
  const context = useContext(DemoContext);
  if (!context) throw new Error("useDemo must be used inside DemoProvider");
  return context;
}

export function resetDemo(dispatch: React.Dispatch<Action>) {
  clearStored();
  dispatch({ type: "reset" });
}
