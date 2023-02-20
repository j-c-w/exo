mod skeleton;

pub enum FillType {
	Exhaustive,
}

pub trait Token {
	fn fill(&self, FillType) -> Vec<&str>;
}

trait PrintableType {
	fn print(&self) -> str;
}

// This is a class of holes.
// A hole has a name (optinally empty),
// a class (which specifies what set
// of values we can use)
// and a set of Holes on which it is
// conditional.
pub struct Hole {
	name: Option<str>,
	class: str,
	conditional: Vec<&str>
}

pub struct StringToken {
	value: str
}

// This is a class that can be used
// to fill a hole. TODO --- need to support
// different distributions of inputs.
pub struct Class<T: PrintableType> {
	name: str,
	values: Vec<&T>
}

impl Token for StringToken {
	fn fill(&self, fill_type) {
		vec![&self.value]
	}
}
