import { db } from '$lib/schema';
import type { ColumnDef } from '@tanstack/table-core';


type Data = {
	header: string;
	accessorKey: string;
}

export async function load() {
	const results = await db.$client.execute("PRAGMA table_info(products);");
	const columns = results.rows.map(row => ({header: row.name, accessorKey: row.name})) as Data[];
	const products = await db.query.products.findMany({
	columns: {
		"ean /Upc /Jan": false,
		model: false,
		topSeller: false,
		monitorCable: false,
		controls: false,
		others: false,
		isvCertifications: false,
	},
	extras: {

	},
	limit: 100,
	offset: 0,
});
	return {
		columns: columns satisfies ColumnDef<Data, string>[],
		products,
	};
};
