#![allow(clippy::collapsible_if, clippy::new_without_default, unused_parens, clippy::needless_return, clippy::len_without_is_empty)]

pub mod keyboard;
pub mod japanese;

use std::cell::RefCell;
use std::collections::HashMap;
use std::fmt::Display;
use std::io::Write;
use std::rc::Rc;
use std::time::Duration;
use serialport::SerialPort;

use japanese::KanaDictionary;


fn main() {

    keyboard::send_keys("あ");
    return;
    let ports = serialport::available_ports().expect("No ports found!");
    for p in &ports {
        println!("{}", p.port_name);
    }

    println!("{}", &ports[0].port_name);
    let port_filename = &ports[0].port_name; //"/dev/ttyACM0";

    let mut port = serialport::new(port_filename, 9600)
        .timeout(Duration::from_millis(10))
        .open()
        .expect("Failed to open port");

    let mut machine = Machine::new();

    loop {
        let stroke = read_stroke(port.as_mut());
        let Command(backspaces, emit_word) = machine.apply(stroke);

        keyboard::send_backspaces(backspaces as u8);
        for _ in 0..backspaces {
            print!("\x08");
        }

        keyboard::send_keys(&emit_word);
        print!("{emit_word}");
        std::io::stdout().flush().unwrap();
    }
}

pub struct PrefixTree(RefCell<(Option<String>, HashMap<Stroke, Rc<PrefixTree>>)>);

impl PrefixTree {
    pub fn new(map: HashMap<Outline, String>) -> Self {
        let tree = PrefixTree(RefCell::new((None, HashMap::new())));
        for (outline, word) in map.into_iter() {
            tree.add(outline.strokes(), word);
        }
        tree
    }

    fn add(&self, strokes: &[Stroke], word: String) {
        let PrefixTree(refcell) = self;
        if strokes.is_empty() {
            let curr_word = &mut refcell.borrow_mut().0;
            curr_word.replace(word);
        } else {
            let children = &mut refcell.borrow_mut().1;
            let head = strokes[0].clone();
            let tail = &strokes[1..];

            if children.contains_key(&head) {
                let child = children[&head].clone();
                child.add(tail, word);
            } else {
                children.insert(head.clone(), Rc::new(PrefixTree(RefCell::new((None, HashMap::new())))));
                children[&head].add(tail, word);
            }
        }
    }

    pub fn lookup(&self, outline: Outline) -> Option<String> {
        self.lookup_by_strokes(outline.strokes())
    }

    fn lookup_by_strokes(&self, strokes: &[Stroke]) -> Option<String> {
        let PrefixTree(refcell) = self;
        if strokes.is_empty() {
            let curr_word  = &refcell.borrow().0;
            curr_word.clone()
        } else {
            let children = &refcell.borrow().1;
            let head = strokes[0].clone();
            let tail = &strokes[1..];
            let child = children[&head].clone();
            child.lookup_by_strokes(tail)
        }

    }
}

pub fn prefix_tree_from_json_dictionary(dictionary: JsonDictionary) -> PrefixTree {
    let JsonDictionary(map) = dictionary;
    let map: HashMap<Outline, String> = map.iter().map(|(k, v)| {
        eprintln!("{k}");
        (Outline::try_from_string(k).unwrap(), v.clone())
    }).collect();
    PrefixTree::new(map)
}


const MAX_UNDO: usize = 1 << 15;


pub struct Machine {
    undo: Vec<Outline>,
    dictionary: Box<dyn Dictionary>,
}


impl Machine {
    pub fn new() -> Self { 
        let filename: &str = "../output/main.json";
//        let dictionary = Box::new(JsonDictionary::load_from_file(filename).unwrap());
        let dictionary = Box::new(KanaDictionary::new());
        Self { 
            undo: Vec::new(), 
            dictionary
        }
    }

    fn current_outline(&self, stroke: Stroke) -> Outline {
       if self.undo.is_empty() {
            Outline::from(stroke)
        } else {
           let previous_outline = self.undo[self.undo.len() - 1].clone();
           previous_outline / stroke
        }
    }

    fn limit_undo(&mut self) {
        if self.undo.len() > MAX_UNDO {
            self.undo = self.undo[self.undo.len() / 2..].to_vec();
        }
    }

    fn apply_lookup(&mut self, stroke: Stroke) -> Command {
//        let outline = self.current_outline();
        let outline = Outline::from(stroke);
        if let Some(word) = self.dictionary.lookup(outline) {
            Command(0, word.to_owned())
        } else {
            Command(0, String::new())
        }
    }

    fn apply_undo(&mut self) -> Command {
        Command(0, String::from("Hello"))
    }

    pub fn apply(&mut self, stroke: Stroke) -> Command {
        self.limit_undo();

        if stroke == Stroke::new(&[Key::MiddleStar]) {
            self.apply_undo()
        } else {
            self.apply_lookup(stroke)
        }
    }
}

#[derive(Clone, Eq, PartialEq, PartialOrd, Ord, Hash, Debug)]
pub struct Outline(Vec<Stroke>);

impl Outline {
    pub fn from(stroke: Stroke) -> Self {
        Outline(vec![stroke])
    }

    pub fn strokes(&self) -> &[Stroke] {
        let Outline(strokes) = self;
        strokes
    }

    pub fn try_from(strokes: &[Stroke]) -> Option<Self> {
        if strokes.is_empty() {
            None
        } else {
            Some(Outline(strokes.to_owned()))
        }
    }


    pub fn len(&self) -> usize {
        self.strokes().len()
    }

    pub fn try_from_string(s: &str) -> Option<Outline> {
        let strokes: Vec<&str> = s.split('/').collect();
        let first = strokes.get(0)?;
        let mut outline = Outline::from(Stroke::try_from_string(first)?);

        for stroke in &strokes[1..] {
            outline = outline / Stroke::try_from_string(stroke)?;
        }

        Some(outline)
    }
}

fn char_to_key(ch: char, right_side: bool) -> Option<Key> {
    let iter: Vec<_> = if right_side {
        KEY_CHARS.iter().rev().collect()
    } else {
        KEY_CHARS.iter().collect()
    };

    for (target_key, letter) in  iter {
        if ch == *letter {
            return Some(*target_key);
        }
    }
    None
}

const MIDDLE_CHARS: &[char] = &['A', 'O', '*', 'E', 'U'];

impl std::ops::Div for Outline {
    type Output = Outline;

    fn div(self, rhs: Self) -> Self::Output {
        let Outline(self_strokes) = self;
        let Outline(rhs_strokes) = &rhs;
        let result_strokes: Vec<Stroke> = self_strokes.iter().chain(rhs_strokes.iter()).cloned().collect();
        Outline(result_strokes)
    }
}

impl std::ops::Div<Stroke> for Outline {
    type Output = Outline;

    fn div(self, rhs: Stroke) -> Self::Output {
        let Outline(self_strokes) = self;
        let mut result_strokes: Vec<Stroke> = self_strokes.clone();
        result_strokes.push(rhs);
        Outline(result_strokes)
    }
}

impl From<Stroke> for Outline {
    fn from(stroke: Stroke) -> Self {
        Outline(vec![stroke])
    }
}

impl Display for Outline {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        let strokes = self.strokes();
        for (i, stroke) in strokes.iter().enumerate() {
            if i > 0 {
                write!(f, "/{stroke}")?;
            } else {
                write!(f, "{stroke}")?;
            }
        }
        Ok(())
    }
}

pub trait Dictionary {
    fn lookup(&self, outline: Outline) -> Option<&str>;
}

pub struct JsonDictionary(HashMap<String, String>);

impl JsonDictionary {
    pub fn load_from_file<P: AsRef<std::path::Path>>(filepath: P) -> Result<Self, Box<dyn std::error::Error>> {
        let dictionary_json = std::fs::read_to_string(filepath)?;
        let dictionary: HashMap<String, String> = serde_json::from_str(&dictionary_json)?;
        Ok(JsonDictionary(dictionary))
    }
}

impl Dictionary for JsonDictionary {
    fn lookup(&self, outline: Outline) -> Option<&str> {
        let JsonDictionary(dictionary) = self;
        let entry = dictionary.get(&outline.to_string());
        entry.map(|s| s.as_str())
    }
}

#[derive(Clone, Eq, PartialEq, PartialOrd, Ord, Hash, Debug)]
pub struct Command(pub usize, pub String);

#[derive(Clone, Eq, PartialEq, PartialOrd, Ord, Hash, Debug)]
pub struct Stroke(Vec<Key>);

impl Stroke {
    pub fn new(keys: &[Key]) -> Self {
        let mut key_vec: Vec<Key> = keys.to_vec();
        key_vec.sort();
        key_vec.dedup();
        Stroke(key_vec)
    }

    pub fn to_outline(self) -> Outline {
        Outline(vec![self])
    }

    pub fn try_from_string(s: &str) -> Option<Self> {
        let mut left_side = true;
        let mut keys: Vec<Key> = vec![];

        for ch in s.chars() {
            if ch == '-' {
                left_side = false;
                continue;
            }
            if MIDDLE_CHARS.contains(&ch) {
                left_side = false;
            }
            let key = char_to_key(ch, !left_side)?;
            keys.push(key);

        }
        Some(Stroke::new(&keys))
    }

    pub fn keys(&self) -> &[Key] {
        let Stroke(keys) = self;
        keys
    }
}

#[cfg(test)]
mod test {
    use super::*;

    #[test]
    fn test() {
        let keys = &[
            Key::LeftS,
            Key::LeftT,
            Key::LeftK,
            Key::MiddleA,
            Key::RightS,
        ];
        assert_eq!(Stroke::try_from_string("STKAS"), Some(Stroke::new(keys)));

        let keys = &[
            Key::LeftS,
            Key::LeftT,
            Key::LeftK,
            Key::RightS,
        ];
        assert_eq!(Stroke::try_from_string("STK-S"), Some(Stroke::new(keys)));
    }


    #[test]
    fn test3() {
        assert!(Outline::try_from_string("KAT").is_some());
        assert!(Outline::try_from_string("BAT/TER").is_some());
    }

    #[test]
    fn test2() {
        let filename: &str = "../dictionaries/base.json";
        let dictionary = JsonDictionary::load_from_file(filename).unwrap();
        let prefix_tree = prefix_tree_from_json_dictionary(dictionary);
//        let outline = Outline::try_from_string("KAT").unwrap();
//        assert_eq!(prefix_tree.lookup(outline), Some("cat".to_owned()));
    }
}


impl std::fmt::Display for Stroke {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        let Stroke(keys) = self;
        let mut has_middle = false;

        for key in keys {
            let side = key_side(*key);
            if side == KeySide::Middle {
                has_middle = true;
            } else if side == KeySide::Right {
                if !has_middle {
                    write!(f, "-")?;
                    has_middle = true;
                }
            }

            write!(f, "{}", key_letter(*key))?;
        }
        Ok(())
    }
}

#[derive(Clone, Copy, Eq, PartialEq, PartialOrd, Ord, Hash, Debug)]
pub enum Key {
    LeftS,
    LeftT,
    LeftK,
    LeftP,
    LeftW,
    LeftH,
    LeftR,

    MiddleA,
    MiddleO,
    MiddleStar,
    MiddleE,
    MiddleU,

    RightF,
    RightR,
    RightP,
    RightB,
    RightL,
    RightG,
    RightT,
    RightS,
    RightD,
    RightZ,

}

#[derive(Clone, Copy, Eq, PartialEq, PartialOrd, Ord, Hash, Debug)]
enum KeySide {
    Left,
    Middle,
    Right,
}

fn key_side(key: Key) -> KeySide {
    for (target_key, side) in KEY_SIDES {
        if key == *target_key {
            return *side;
        }
    }
    unreachable!()
}

fn key_letter(key: Key) -> char {
    for (target_key, letter) in KEY_CHARS {
        if key == *target_key {
            return *letter;
        }
    }
    unreachable!()

}

const KEY_CHARS: &[(Key, char)] = &[
    (Key::LeftS, 'S'),
    (Key::LeftT, 'T'),
    (Key::LeftK, 'K'),
    (Key::LeftP, 'P'),
    (Key::LeftW, 'W'),
    (Key::LeftH, 'H'),
    (Key::LeftR, 'R'),

    (Key::MiddleA, 'A'),
    (Key::MiddleO, 'O'),
    (Key::MiddleStar, '*'),
    (Key::MiddleE, 'E'),
    (Key::MiddleU, 'U'),

    (Key::RightF, 'F'),
    (Key::RightR, 'R'),
    (Key::RightP, 'P'),
    (Key::RightB, 'B'),
    (Key::RightL, 'L'),
    (Key::RightG, 'G'),
    (Key::RightT, 'T'),
    (Key::RightS, 'S'),
    (Key::RightD, 'D'),
    (Key::RightZ, 'Z'),
];

const KEY_SIDES: &[(Key, KeySide)] = &[
    (Key::LeftS, KeySide::Left),
    (Key::LeftT, KeySide::Left),
    (Key::LeftK, KeySide::Left),
    (Key::LeftP, KeySide::Left),
    (Key::LeftW, KeySide::Left),
    (Key::LeftH, KeySide::Left),
    (Key::LeftR, KeySide::Left),

    (Key::MiddleA, KeySide::Middle),
    (Key::MiddleO, KeySide::Middle),
    (Key::MiddleStar, KeySide::Middle),
    (Key::MiddleE, KeySide::Middle),
    (Key::MiddleU, KeySide::Middle),

    (Key::RightF, KeySide::Right),
    (Key::RightR, KeySide::Right),
    (Key::RightP, KeySide::Right),
    (Key::RightB, KeySide::Right),
    (Key::RightL, KeySide::Right),
    (Key::RightG, KeySide::Right),
    (Key::RightT, KeySide::Right),
    (Key::RightS, KeySide::Right),
    (Key::RightD, KeySide::Right),
    (Key::RightZ, KeySide::Right),
];

const KEY_CODES: &[(Key, u64)] = &[
    (Key::LeftS, 0x000000002080),
    (Key::LeftT, 0x000000001080),
    (Key::LeftK, 0x000000000880),
    (Key::LeftP, 0x000000000480),
    (Key::LeftW, 0x000000000280),
    (Key::LeftH, 0x000000000180),
    (Key::LeftR, 0x000000400080),

    (Key::MiddleA, 0x000000200080),
    (Key::MiddleO, 0x000000100080),
    (Key::MiddleStar, 0x000000080080),
    (Key::MiddleStar, 0x000020000080),
    (Key::MiddleStar, 0x000000040080),
    (Key::MiddleStar, 0x000010000080),
    (Key::MiddleE, 0x000008000080),
    (Key::MiddleU, 0x000004000080),

    (Key::RightF, 0x000002000080),
    (Key::RightR, 0x000001000080),
    (Key::RightP, 0x004000000080),
    (Key::RightB, 0x002000000080),
    (Key::RightL, 0x001000000080),
    (Key::RightG, 0x000800000080),
    (Key::RightT, 0x000400000080),
    (Key::RightS, 0x000200000080),
    (Key::RightD, 0x000100000080),
    (Key::RightZ, 0x010000000080),
];

fn read_stroke(port: &mut dyn SerialPort) -> Stroke {
    let mut buf = [0; 6];
    let mut total_amount = 0;

    loop {
        let buf_slice = &mut buf[total_amount..6];
        match port.read(buf_slice) {
            Ok(amount) => {
                total_amount += amount;
            },
            Err(_e) => {
            }
        }

        if total_amount == 6 {
            break;
        }
    }

    let value: u64 =
        (buf[0] as u64) |
        (buf[1] as u64) << 8 |
        (buf[2] as u64) << 16 |
        (buf[3] as u64) << 24 |
        (buf[4] as u64) << 32 |
        (buf[5] as u64) << 40;

    let mut keys = vec![];
    for (key, key_value) in KEY_CODES {
        if value & key_value == *key_value {
            keys.push(*key);
        }
    }

    Stroke::new(keys.as_slice())
}
