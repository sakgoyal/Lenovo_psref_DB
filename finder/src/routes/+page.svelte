<script lang="ts">
	import "../app.css";
	import DataTable from "./data-table.svelte";
	import ColumnFilter from "./ColumnFilter.svelte";
	import * as duckdb from "@duckdb/duckdb-wasm";
	import duckdb_wasm from "@duckdb/duckdb-wasm/dist/duckdb-mvp.wasm?url";
	import mvp_worker from "@duckdb/duckdb-wasm/dist/duckdb-browser-mvp.worker.js?url";
	import duckdb_wasm_eh from "@duckdb/duckdb-wasm/dist/duckdb-eh.wasm?url";
	import eh_worker from "@duckdb/duckdb-wasm/dist/duckdb-browser-eh.worker.js?url";

	const MANUAL_BUNDLES: duckdb.DuckDBBundles = {
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
	const logger = new duckdb.ConsoleLogger();
	const db = new duckdb.AsyncDuckDB(logger, worker);
	window.db = db; // Expose db for debugging
	await db.instantiate(bundle.mainModule, bundle.pthreadWorker);
	const conn = await db.connect();
	await conn.query(`IMPORT DATABASE 'http://localhost:5173/export';`);
	// const res = (await conn.query("SELECT * FROM products LIMIT 10")).toArray().map((r) => Object.fromEntries(r));
</script>

<svelte:head>
	<title>Lenovo Finder</title>
	<meta name="description" content="Advanced data table with filtering, sorting, pagination, and column management" />
</svelte:head>

<div class="p-5 grid grid-cols-3 gap-x-3">
	<!-- {#await getFilterValues()}
		<p>Loading...</p>
	{:then filterValues}
		{#each filterValues as filterValue}
			<ColumnFilter filterName={filterValue.column_name} options={filterValue.value} />
		{/each}
	{:catch error}
		<p>Error: {error.message}</p>
	{/await} -->
</div>
<div class="w-90% h-dvh">
	<!-- <DataTable {columns} data={data.products} /> -->
</div>
