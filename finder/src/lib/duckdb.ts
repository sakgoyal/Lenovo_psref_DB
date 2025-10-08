import duckdb_wasm from '@duckdb/duckdb-wasm/dist/duckdb-mvp.wasm?url';
import mvp_worker from '@duckdb/duckdb-wasm/dist/duckdb-browser-mvp.worker.js?url';
import duckdb_wasm_eh from '@duckdb/duckdb-wasm/dist/duckdb-eh.wasm?url';
import eh_worker from '@duckdb/duckdb-wasm/dist/duckdb-browser-eh.worker.js?url';
import duckdb_wasm_coi from '@duckdb/duckdb-wasm/dist/duckdb-coi.wasm?url';
import coi_worker from '@duckdb/duckdb-wasm/dist/duckdb-browser-coi.worker.js?url';
import coi_pthread_worker from '@duckdb/duckdb-wasm/dist/duckdb-browser-coi.pthread.worker.js?url';
import type { AsyncDuckDBConnection, DuckDBBundles } from '@duckdb/duckdb-wasm';
import { browser } from '$app/environment';
import * as duckdb from '@duckdb/duckdb-wasm';

let conn: AsyncDuckDBConnection | null = null;

export async function instantiateDuckDb(): Promise<AsyncDuckDBConnection> {

  if (conn) {
    return conn;
  }

  if (!browser) {
    Error("Can only instantiate DuckDB from browser.")
  }



  const MANUAL_BUNDLES: DuckDBBundles = {
    mvp: {
      mainModule: duckdb_wasm,
      mainWorker: mvp_worker,
    },
    eh: {
      mainModule: duckdb_wasm_eh,
      mainWorker: eh_worker,
    },
    coi: {
      mainModule: duckdb_wasm_coi,
      mainWorker: coi_worker,
      pthreadWorker: coi_pthread_worker,
    }
  };
  // Select a bundle based on browser checks
  const bundle = await duckdb.selectBundle(MANUAL_BUNDLES);
  // Instantiate the asynchronus version of DuckDB-wasm
  const worker = new Worker(bundle.mainWorker!);
  const logger = new duckdb.VoidLogger();
  const db = new duckdb.AsyncDuckDB(logger, worker);
  await db.instantiate(bundle.mainModule, bundle.pthreadWorker);
  conn = await db.connect();
  await conn.query(`IMPORT DATABASE '${window.location.origin}/export';`);

  return conn;
}
