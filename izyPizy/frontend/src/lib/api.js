// All fetch() wrappers for the IZY PIZY API will go here

const BASE = '/api'

export async function fetchJson(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, options)
  if (!res.ok) throw new Error(`API error: ${res.status}`)
  return res.json()
}
