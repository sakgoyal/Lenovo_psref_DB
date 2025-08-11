import { drizzle } from 'drizzle-orm/libsql';
import { DatabaseSync } from 'node:sqlite';
const database = new DatabaseSync('C:/Users/Saksham/Documents/projects/black_hole/products.db', {readOnly: true });


const db = drizzle({
	connection: {
		url: 'file:../products.db',
	},
});


export async function load() {

	const results = await db.$client.execute("PRAGMA table_info(products);")
	const columns = results.rows.map(row => row.name)
	return {
		post: {
			cols: columns,
		}
	};
};
