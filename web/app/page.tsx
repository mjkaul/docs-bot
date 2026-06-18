import TabShell from "./components/TabShell";
import { buildPageTree } from "@/lib/pageTree";

export default function Home() {
  const tree = buildPageTree();
  return (
    <div className="h-full flex flex-col">
      <TabShell tree={tree} />
    </div>
  );
}
