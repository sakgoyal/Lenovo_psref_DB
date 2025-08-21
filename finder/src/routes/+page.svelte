<script lang="ts">
	import "../app.css";
	import { instantiateDuckDb } from "$lib/duckdb";
	import { Table } from "@flowbite-svelte-plugins/datatable";
	import { Button, Label } from "flowbite-svelte";
	import Svelecte from "svelecte";
	import { filters } from "./data";
	import { pushState } from "$app/navigation";
	import { onMount } from "svelte";

	const conn = instantiateDuckDb();
	async function get_data() {
		const data = (await (await conn).query("SELECT * FROM products LIMIT 100")).toArray().map((r) => Object.fromEntries(r));
		return data;
	}

	async function applyFilters(data: Record<string, string[]>) {
		const queryParts = [];
		for (const [key, values] of Object.entries(data)) {
			if (values.length > 0) {
				queryParts.push(`"${key}" IN (${values.map((v) => `'${v}'`).join(", ")})`);
			}
		}
		const query = `SELECT * FROM products ${queryParts.length > 0 ? "WHERE " + queryParts.join(" AND ") : ""} LIMIT 100`;
		console.log("Executing query:", query);
		const ret = (await (await conn).query(query)).toArray().map((r) => Object.fromEntries(r));
		console.log("Query result:", ret);
		return ret;
	}

	async function handleFormSubmit(event?: SubmitEvent) {
		event?.preventDefault();
		const formData = new FormData(event?.currentTarget as HTMLFormElement);
		const obj: Record<string, string[]> = {};
		for (const [k, v] of formData) (obj[k] ??= []).push(v as string);
		const urlParams = new URLSearchParams();
		for (const [key, values] of Object.entries(obj)) {
			if (values.length > 0) {
				for (const value of values) {
					urlParams.append(key, value);
				}
			} else {
				urlParams.delete(key);
			}
		}
		pushState(`?${urlParams.toString()}`, {
			urlParams: urlParams.toString(),
		});
		console.log("Form submitted with data:", obj);
		data = applyFilters(obj);
	}

	onMount(() => {
		const urlParams = new URLSearchParams(window.location.search);
		urlParams.forEach((value, key) => {
			if (form_data[key]) {
				form_data[key] = [...form_data[key], value];
			} else {
				form_data[key] = [value];
			}
		});
		handleFormSubmit();
	});
	let form_data = $state<Record<string, string[]>>(
		Object.keys(filters).reduce(
			(acc, key) => {
				acc[key] = [];
				return acc;
			},
			{} as Record<string, string[]>,
		),
	);
	let data = $state(get_data());
</script>

<div class="min-w-[300px]  pr-5">
	<form method="POST" onsubmit={handleFormSubmit} id="filter_form" class="dark">
		{#each Object.entries(filters) as [column_name, options]}
			<Label>{column_name}</Label>
			<Svelecte class="dark" name={column_name} bind:value={form_data[column_name]} {options} multiple clearable keepSelectionInList={true} />
		{/each}
		<Button type="submit">Apply Filters</Button>
	</form>
</div>
<div class="">
	{#await data}
		<p>Loading data...</p>
	{:then data}
		<Table items={data} dataTableOptions={{fixedColumns: false}}/>
	{/await}
</div>


<style>
	.dark {
		--sv-min-height: 40px;
		--sv-bg: #32363f;
		--sv-disabled-bg: #eee;
		--sv-border: 1px solid #626262;
		--sv-border-radius: 4px;
		--sv-general-padding: 4px;
		--sv-control-bg: var(--sv-bg);
		--sv-item-wrap-padding: 3px 3px 3px 6px;
		--sv-selection-wrap-padding: 3px 3px 3px 4px;
		--sv-selection-multi-wrap-padding: 3px 3px 3px 6px;
		--sv-item-selected-bg: #626262;
		--sv-item-btn-color: #ccc;
		--sv-item-btn-color-hover: #ccc;
		--sv-item-btn-bg: #626262;
		--sv-item-btn-bg-hover: #bc6063;
		--sv-icon-color: #bbb;
		--sv-icon-color-hover: #ccc;
		--sv-icon-bg: transparent;
		--sv-icon-size: 20px;
		--sv-separator-bg: #626262;
		--sv-btn-border: 0;
		--sv-placeholder-color: #ccccd6;
		--sv-dropdown-bg: var(--sv-bg);
		--sv-dropdown-border: var(--sv-border);
		--sv-dropdown-offset: 1px;
		--sv-dropdown-width: auto;
		--sv-dropdown-shadow: 0 1px 3px #555;
		--sv-dropdown-height: 320px;
		--sv-dropdown-active-bg: #553d3d;
		--sv-dropdown-selected-bg: #754545;
		--sv-create-kbd-border: 1px solid #626262;
		--sv-create-kbd-bg: #626262;
		--sv-create-disabled-bg: #fcbaba;
		--sv-loader-border: 2px solid #626262;
	}
</style>
