#![allow(non_snake_case, unused)]
use dioxus::prelude::*;

fn main() {
    launch(app)
}

fn app() -> Element {
    let mut count = use_signal(|| 0);
    rsx! {
        h1 { "Counter {count}"}
        button { onclick: move |_| count +=1, "+"}
        button { onclick: move |_| count -=1, "-"}
    }
}
