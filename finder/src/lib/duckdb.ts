import duckdb_wasm from '@duckdb/duckdb-wasm/dist/duckdb-mvp.wasm?url';
import mvp_worker from '@duckdb/duckdb-wasm/dist/duckdb-browser-mvp.worker.js?url';
import duckdb_wasm_eh from '@duckdb/duckdb-wasm/dist/duckdb-eh.wasm?url';
import eh_worker from '@duckdb/duckdb-wasm/dist/duckdb-browser-eh.worker.js?url';
import type { AsyncDuckDBConnection, DuckDBBundles } from '@duckdb/duckdb-wasm';
import { browser } from '$app/environment';

let conn: AsyncDuckDBConnection | null = null;

export async function instantiateDuckDb(): Promise<AsyncDuckDBConnection> {

  if (conn) {
    return conn;
  }

  if (!browser) {
    Error("Can only instantiate DuckDB from browser.")
  }

  const duckdb = await import('@duckdb/duckdb-wasm');

  const MANUAL_BUNDLES: DuckDBBundles = {
    mvp: {
      mainModule: duckdb_wasm,
      mainWorker: mvp_worker,
    },
    eh: {
      mainModule: duckdb_wasm_eh,
      mainWorker: eh_worker,
    },
  };
  // Select a bundle based on browser checks
  const bundle = await duckdb.selectBundle(MANUAL_BUNDLES);
  // Instantiate the asynchronus version of DuckDB-wasm
  const worker = new Worker(bundle.mainWorker!);
  const logger = new duckdb.VoidLogger();
  const db = new duckdb.AsyncDuckDB(logger, worker);
  await db.instantiate(bundle.mainModule, bundle.pthreadWorker);
  conn = await db.connect();
  await conn.query(`IMPORT DATABASE 'http://localhost:5173/export';`);

  return conn;
}
