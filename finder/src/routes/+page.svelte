<script lang="ts">
	import "../app.css";
	// import DataTable from "./data-table.svelte";
	import { instantiateDuckDb } from "$lib/duckdb";
	import { Table } from "@flowbite-svelte-plugins/datatable";

	const conn = await instantiateDuckDb();
	async function get_data() {
		const data = (await conn.query("SELECT * FROM products LIMIT 100")).toArray().map((r) => Object.fromEntries(r));
		return data;
	}

	$inspect({
		params: window.location.search,
	})
</script>

<div class="">
	<!-- <DataTable {columns} data={data.products} /> -->

	{#await get_data()}
		<p>Loading data...</p>
	{:then data}
		<Table items={data} />
	{/await}
</div>
