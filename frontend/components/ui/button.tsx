import * as React from "react";
import { Slot } from "@radix-ui/react-slot";
import { cn } from "@/lib/utils";
export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {asChild?:boolean}
export const Button = React.forwardRef<HTMLButtonElement,ButtonProps>(({className,asChild=false,...props},ref)=>{
 const Comp=asChild?Slot:"button";
 return <Comp ref={ref} className={cn("rounded-lg bg-emerald-700 px-4 py-2 font-medium text-white disabled:opacity-50",className)} {...props}/>;
});
Button.displayName="Button";
