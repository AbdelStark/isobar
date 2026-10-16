import type {JsonRecord} from './core';

export type Actor = JsonRecord & { id: string; name: string; strategy: string };
export type Scenario = JsonRecord & {
  id: string; name: string; description: string; question: string; classification: string;
  seed: number; horizon: number; actors: Actor[]; policy: JsonRecord; verification: JsonRecord;
};
export type Frame = { tick: number; actors: Actor[]; institution: JsonRecord; metrics: JsonRecord };
export type Event = { id: string; tick: number; kind: string; actor_id: string | null; summary: string; causes: string[]; data: JsonRecord; visibility: string };
export type Run = { id: string; status: string; scenario: Scenario; model_version: string; completed_ticks: number; frames: Frame[]; events: Event[]; metrics: JsonRecord; warnings: unknown[]; branch: JsonRecord | null; terminal_cause: string | null; digests: JsonRecord };
