import api from "./client";

export interface TPDispute {
  id: number;
  name: string;
  verdict_number: string;
  verdict: string;
  dispute: string;
  legal_basis: string;
  djp: string;
  taxpayer: string;
  assembly_decision: string;
  created_at: string;
  updated_at: string;
}

export type TPDisputeInput = Omit<TPDispute, "id" | "created_at" | "updated_at">;

export async function listTPDisputes(): Promise<TPDispute[]> {
  const { data } = await api.get<TPDispute[]>("/tp-disputes/");
  return data;
}

export async function createTPDispute(input: TPDisputeInput): Promise<TPDispute> {
  const { data } = await api.post<TPDispute>("/tp-disputes/", input);
  return data;
}

export async function updateTPDispute(id: number, input: Partial<TPDisputeInput>): Promise<TPDispute> {
  const { data } = await api.patch<TPDispute>(`/tp-disputes/${id}/`, input);
  return data;
}

export async function deleteTPDispute(id: number): Promise<void> {
  await api.delete(`/tp-disputes/${id}/`);
}