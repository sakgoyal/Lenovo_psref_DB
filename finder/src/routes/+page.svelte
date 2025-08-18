<script lang="ts">
	import "../app.css";
	// import DataTable from "./data-table.svelte";
	import { instantiateDuckDb } from "$lib/duckdb";
	import ColumnFilter from "./ColumnFilter.svelte";

	async function load_db() {
		// A simple case of a db of a single parquet file.
		const db = await instantiateDuckDb();
		const conn = await db.connect();
		await conn.query(`IMPORT DATABASE 'http://localhost:5173/export';`);

		window.conn = conn; // Expose conn for debugging
		return conn;
	}

	// Set up the db connection as an empty promise.
	const conn_prom = load_db();

	async function get_filters() {
		const conn = await conn_prom;
		const filterValues = (await conn.query("SELECT * FROM filter_values WHERE column_name NOT IN ('Optical', 'Docking', 'Included Upgrade', 'Announce Date', 'Display', 'Standard Ports', 'Operating System', 'Dimensions (WxDxH)', 'Product', 'Processor', 'End of Support');"))
			.toArray()
			.map((r) => Object.fromEntries(r)) as { column_name: string; options: string[] }[];

		filterValues.forEach((column, i) => { filterValues[i].options = JSON.parse(column.options) as string[]; })
		// remove null values from options
		filterValues.forEach((column, i) => {
			filterValues[i].options = filterValues[i].options.filter((option) => option !== null);
		});

		return filterValues;
	}

	// const res = (await conn.query("SELECT * FROM products LIMIT 10")).toArray().map((r) => Object.fromEntries(r));
</script>

<svelte:head>
	<title>Lenovo Finder</title>
	<meta name="description" content="Advanced data table with filtering, sorting, pagination, and column management" />
</svelte:head>

<div class="p-5 grid grid-cols-3 gap-x-3">
	{#await get_filters()}
		<p>Loading...</p>
	{:then filterValues}
		{#each filterValues as filterValue}
			<ColumnFilter filterName={filterValue.column_name} options={filterValue.options} />
		{/each}
	{:catch error}
		<p>Error: {error.message}</p>
	{/await}
</div>
<div class="w-90% h-dvh">
	<!-- <DataTable {columns} data={data.products} /> -->
</div>
